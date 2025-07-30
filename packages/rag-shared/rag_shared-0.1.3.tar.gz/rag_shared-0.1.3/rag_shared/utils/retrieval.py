import openai
from typing import Optional, Any, Dict, List
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorQuery

from azure.search.documents.models import VectorizedQuery, VectorizableTextQuery, VectorQuery
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration
)
from rag_shared.utils.config import Config
from datetime import datetime

class Retrieval:
    def __init__(
        self,
        *,
        config: Config
    ):
        self.config: Config = config
        # ─── Azure Search clients (Admin) ─────────────────────────────────
        self.cred = AzureKeyCredential(self.config.search_key)
        self.index_client = SearchIndexClient(
            endpoint=self.config.search_endpoint,
            credential=self.cred
        )
        self.search_client = SearchClient(
            endpoint=self.config.search_endpoint,
            index_name=self.config.app.index.name,
            credential=self.cred
        )
        # ─── Azure OpenAI clients ─────────────────────────────────────────
        # Embeddings client
        self.openai_embeddings_client = openai.AzureOpenAI(
            api_key=self.config.search_embedding_api_key,
            api_version=self.config.search_embedding_api_version,
            azure_endpoint=self.config.openai_api_base,
            azure_deployment=self.config.search_deployment_name
        )
        # Chat completions client (not used here)
        self.openai_client = openai.AzureOpenAI(
            api_key=self.config.openai_api_key,
            api_version=self.config.openai_api_version,
            azure_endpoint=self.config.openai_api_base,
            azure_deployment=self.config.openai_deployment
        )

    def _document_exists(self, doc_id: str) -> bool:
        """
        Return True if a document with the given key already exists in the index.
        """
        try:
            self.search_client.get_document(key=doc_id)
            return True
        except ResourceNotFoundError:
            return False

    def upload_documents(self, docs: List[dict]) -> List[dict]:
        """
        Upsert documents into the Azure Search index based on their 'id'.
        New docs are created; existing docs are updated.

        Returns the indexing result for all provided documents.
        """
        # Validate documents have 'id'
        for doc in docs:
            if 'id' not in doc:
                raise ValueError("Each document must have an 'id' field.")

        # Perform upsert (mergeOrUpload) for all docs in one call
        result = self.search_client.merge_or_upload_documents(documents=docs)
        return [r.__dict__ for r in result]

    def embed(
        self,
        docs: List[dict]
    ) -> List[dict]:
        # 1) Collect texts
        texts = [d[self.config.app.index.index_text_field] for d in docs]

        # 2) Call the Azure OpenAI embeddings API
        resp = self.openai_embeddings_client.embeddings.create(
            model=self.config.search_deployment_name,
            input=texts
        )
        if not resp or not hasattr(resp, 'data') or not isinstance(resp.data, list):
            raise ValueError("Invalid response from embeddings API.")
        if not resp.data:
            raise ValueError("No embeddings returned.")

        # 3) Attach embeddings back to the docs
        for doc, emb in zip(docs, resp.data):
            doc[self.config.app.index.vector_field] = emb.embedding

        return docs

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        skip: int = 0,
        filter: Optional[str] = None,
        order_by: Optional[List[str]] = None,
        facets: Optional[List[str]] = None,
        highlight_fields: Optional[List[str]] = None,
        search_fields: Optional[List[str]] = None,
        select_fields: Optional[List[str]] = None,
        include_total_count: bool = False,
        semantic: bool = False,
        semantic_config: Optional[str] = None,
        vector_search: bool = False,
        hybrid: Optional[float] = None,
        vector_field: str = "contentVector",
    ) -> Dict[str, Any]:
        is_vector_only = vector_search and hybrid is None
        is_hybrid = hybrid is not None

        # Prepare vector queries if needed
        vector_queries = []
        if is_vector_only or is_hybrid:
            # 1) Build a dummy doc for your embedder using your configured text‐field name
            dummy = { self.config.app.index.index_text_field: query }
            docs_with_vec = self.embed([ dummy ])
            
            # 2) Pull the embedding back out from your configured vector‐field name
            vec = docs_with_vec[0][ self.config.app.index.vector_field ]

            # 3) Build the VectorQuery, again using your configured vector field
            vector_query = VectorizedQuery(
                vector=vec,
                k_nearest_neighbors=top_k,
                fields=self.config.app.index.vector_field
            )
            if is_hybrid:
                vector_query.weight = hybrid

            vector_queries.append(vector_query)

        search_text = '*' if is_vector_only else query
        qtype = 'semantic' if semantic else None
        sem_conf = semantic_config if semantic else None
        effective_highlight_fields = None if is_vector_only else highlight_fields

        results = self.search_client.search(
            search_text=search_text,
            filter=filter,
            order_by=order_by,
            facets=facets,
            highlight_fields=','.join(effective_highlight_fields) if effective_highlight_fields else None,
            search_fields=search_fields,
            select=select_fields,
            top=top_k,
            skip=skip,
            include_total_count=include_total_count,
            vector_queries=vector_queries,
            query_type=qtype,
            semantic_configuration_name=sem_conf,
        )
        
        hits = []
        for doc in results:
            record = dict(doc)
            record['_score'] = doc.get('@search.score')
            hits.append(record)


        return {
            'results': hits,
            'total_count': results.get_count() if include_total_count else None
        }
if __name__ == '__main__':

    config = Config()
    # Mock document for testing
    doc_list = [
        {
            "id": "test-0001",
            "timestamp": datetime.utcnow().timestamp(),  # float seconds
            "text": (
                "Anastasiya (00:01.242)\n"
                "Hi everyone and welcome back to our podcast. … TESTING\n"
            ),
            "questionoranswer": "question",
            "speaker": "Anastasiya",
            "video_url": None,
            "keyword": None,
            "topic": None,
            "filename": "anastasiya-intro"
        }
    ]

    # Upload mock document
    retrieval = Retrieval(config=config)
    results = retrieval.upload_documents(doc_list)
    print("\nUpload results:")
    for r in results:
        print(f"  id={r['key']}, succeeded={r['succeeded']}, status={r['status_code']}")

        
    # Retrieve and display stored document

    print("\nRetrieving uploaded documents:")
    for r in results:
        if r['succeeded']:
            stored = retrieval.search_client.get_document(key=r['key'])
            print(f"\nDocument ID: {r['key']}")
            print(f"  text: {stored['text']}")
            # Print additional fields if present
            for field in ['speaker', 'questionoranswer', 'filename']:
                if field in stored:
                    print(f"  {field}: {stored.get(field)}")
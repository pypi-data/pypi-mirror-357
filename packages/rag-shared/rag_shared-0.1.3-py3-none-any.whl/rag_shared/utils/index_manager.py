import os
import yaml
import logging
from typing import Any, Dict, Optional, Union
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
    AzureOpenAIVectorizer, AzureOpenAIVectorizerParameters,
    SemanticConfiguration, SemanticSearch, SemanticPrioritizedFields, SemanticField,
    SearchIndex
)
from rag_shared.utils.config import Config
from rag_shared.resources import load_index_schema

def load_transcript_data(config: Config) -> Dict[str, Any]:
    """
    Load and return the transcript data (JSON or YAML) as a dict.
    Uses os.path to locate the file based on config.app.transcript settings.
    """
    utils_dir = os.path.dirname(__file__)
    pkg_root = os.path.dirname(utils_dir)

    transcripts_cfg = config.app.index
    transcripts_dir = os.path.join(pkg_root, 'resources', transcripts_cfg.indexes_path)
    transcript_path = os.path.join(transcripts_dir, transcripts_cfg.index_yml_path)

    with open(transcript_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    ext = os.path.splitext(transcripts_cfg.index_yml_path)[1].lower()
    if ext in ['.yml', '.yaml']:
        return yaml.safe_load(raw) or {}
    elif ext == '.json':
        import json
        return json.loads(raw)
    else:
        raise ValueError(f"Unsupported transcript file type: {ext}")



class IndexManager:
    def __init__(self, config: Config):
        """
        :param config: Config instance containing connection info and defaults.
        """
        self.config = config

        # Load and print index schema via helper
        self.schema = load_index_schema(
            config.app.index.indexes_path,
            config.app.index.index_yml_path
        )

        # Load transcript data via helper
        self.transcript_data = load_transcript_data(config)

        # Clients from config
        credential = AzureKeyCredential(config.search_key)
        endpoint   = config.search_endpoint
        self.client         = SearchIndexClient(endpoint=endpoint, credential=credential)
        self.indexer_client = SearchIndexerClient(endpoint=endpoint, credential=credential)

        # Names from config
        self.index_name     = config.app.index.name
        self.skillset_name  = config.app.index.skillset_name
        self.indexer_name   = config.app.index.indexer_name

    def exists(self, index_name: Optional[str] = None) -> bool:
        """Check if the index exists."""
        name = index_name if index_name is not None else self.index_name
        try:
            self.client.get_index(name)
            return True
        except Exception:
            return False

    def create_index(self):
        """Create or update search index using schema from passed YAML or Config."""
        if not self.index_name:
            raise ValueError("Index name must be defined in Config.app.index.name")

        fields_cfg = self.schema.get("fields", [])
        fields = []
        for f in fields_cfg:
            type_str = f.get("type")
            if type_str == "Collection":
                item_type = getattr(SearchFieldDataType, f["item_type"])
                dtype = SearchFieldDataType.Collection(item_type)
            else:
                dtype = getattr(SearchFieldDataType, type_str)

            kwargs = {
                "key": f.get("key", False),
                "searchable": f.get("searchable", False),
                "filterable": f.get("filterable", False),
                "retrievable": f.get("retrievable", True),
                "sortable": f.get("sortable", False)
            }
            if "vector" in f:
                v = f["vector"]
                kwargs.update({
                    "vector_search_dimensions": v.get("dimensions"),
                    "vector_search_profile_name": v.get("profile_name")
                })

            fields.append(SearchField(name=f.get("name"), type=dtype, **kwargs))

        vs = self.schema.get("vector_search", {})
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="hnsw-config")
            ],
            profiles=[
                VectorSearchProfile(
                    name="hnsw-profile",
                    algorithm_configuration_name="hnsw-config",
                    vectorizer_name="azure-oai"
                )
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    vectorizer_name="azure-oai",
                    kind="azureOpenAI",
                    parameters=AzureOpenAIVectorizerParameters(
                        resource_url=self.config.open_ai_endpoint,
                        deployment_name=self.config.search_deployment_name,
                        model_name=self.config.search_embedding_model,
                        api_key=self.config.open_ai_key
                    )
                )
            ]
        )

        semantic_cfg = SemanticConfiguration(
            name="default-semantic",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="text")],
                title_field=SemanticField(field_name="questionoranswer")
            )
        )
        semantic_search = SemanticSearch(configurations=[semantic_cfg])

        definition = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search
        )
        self.client.create_or_update_index(definition)
        print(f"✅ Created/updated index '{self.index_name}'")

    def create_skillset(self):
        """
        Create or update the skillset based on config.indexer_schema.
        """
        # Implementation placeholder, uses self.config.indexer_schema
        pass


if __name__ == '__main__':
    from rag_shared.utils.config import Config
    cfg = Config()
    idx_manager = IndexManager(config = cfg)

    print('Index name: ', idx_manager.index_name)
    print('The default index exists: ', idx_manager.exists())

    if not idx_manager.exists():
        idx_manager.create_index()
    else:
        print(f'Index {cfg.index_name} already exists')

    # idx_manager.create_embedding_skillset()

    # val = idx_manager.indexer_client.get_skillset(cfg.search_skillset_name) is not None

    # print(val)
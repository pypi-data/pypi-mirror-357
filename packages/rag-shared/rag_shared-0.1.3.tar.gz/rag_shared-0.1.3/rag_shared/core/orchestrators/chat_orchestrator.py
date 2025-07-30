from typing import List, Dict, Any, Optional, Sequence
from rag_shared.core.orchestrators.rag_orchestrator import RagOrchestrator
from rag_shared.core.fetchers.base import DataFetcher
from rag_shared.core.models.base import LLMModel
from rag_shared.core.prompt_builders.base import PromptBuilder
from rag_shared.utils.config import Config
from rag_shared.core.fetchers.registry import get_processor

class ChatOrchestrator(RagOrchestrator):
    """
    Extends RagOrchestrator to support multi-turn chats by
    carrying forward history and injecting a persistent system prompt.
    """
    def __init__(
        self,
        fetchers: Sequence[DataFetcher],
        model: LLMModel,
        prompt_builder: PromptBuilder,
        config: Config,
        default_proc: str = "default",
        system_prompt: Optional[str] = None
    ):
        # Pass system_prompt into the base class so it always gets prepended
        super().__init__(
            fetchers=fetchers,
            model=model,
            prompt_builder=prompt_builder,
            config=config,
            system_prompt=system_prompt,
            default_proc=default_proc,
        )
        # Start with an empty history
        self.history: List[Dict[str, str]] = []

    async def __call__(
        self,
        user_question: str,
        fetch_args:    Optional[Dict[str, Dict[str, Any]]] = None,
        history:       Optional[List[Dict[str, str]]]     = None,
        **model_kwargs: Any
    ) -> Dict[str, Any]:
        # If the caller passes a fresh history, respect it; otherwise reuse our stored one
        if history is not None:
            self.history = history.copy()

        # On the very first call (empty history), the base always prepends system_prompt
        result = await super().__call__(
            user_question=user_question,
            fetch_args=fetch_args,
            history=self.history,
            **model_kwargs
        )

        # Update our internal history so next turn will start from here
        self.history = result["history"]
        return result
    
if __name__ == "__main__":

    import asyncio
    import os
    from rag_shared.utils.config import Config
    from rag_shared.core.fetchers.azure_search.azure_search import AzureSearchFetcher
    from rag_shared.core.models.azure_openai import AzureOpenAIModel
    from rag_shared.core.prompt_builders.template import TemplatePromptBuilder

    async def main():
        # 1) Load configuration (env or .env)
        cfg = Config()

        # 2) Instantiate your data fetchers
        azure_fetcher = AzureSearchFetcher(config=cfg)

        # 3) Instantiate your LLM model
        llm_model = AzureOpenAIModel(
            config=cfg)

        # 4) Load prompt template and create PromptBuilder
        builder = TemplatePromptBuilder(cfg)

        # 5) Instantiate the ChatOrchestrator
        orchestrator = ChatOrchestrator(
            fetchers=[azure_fetcher],
            model=llm_model,
            prompt_builder=builder,
            config=cfg,
            system_prompt=cfg.app.llm.params.system_prompt
        )

        # 6) Define fetch arguments template
        common_fetch_args = {
            "AzureSearchFetcher": {
                "query": None,  # will be set per question
                "filter": "",
                "top_k": 5,
                "include_total_count": True,
                "facets": ["speaker,count:5", "topic"],
                "highlight_fields": ["text"],
                "select_fields": [
                    "id","filename","block_id","chunk_index","part","speaker",
                    "timestamp","tokens","video_url","keyword","topic","text"
                ],
                "vector_search": True,
            }
        }

        # 7) Start a multi-turn chat
        history: List[Dict[str, str]] = []

        # First user question
        user_q1 = "Who is David?"
        print(f"\nUser: {user_q1}\n")
        common_fetch_args["AzureSearchFetcher"]["query"] = user_q1
        result1 = await orchestrator(
            user_question=user_q1,
            fetch_args=common_fetch_args,
            history=history
        )
        print(f"Assistant: {result1['answer']}\n")
        history = result1["history"]

        # Second user question, leveraging history
        user_q2 = "What is an eating disorder?"
        print(f"\nUser: {user_q2}\n")
        common_fetch_args["AzureSearchFetcher"]["query"] = user_q2
        result2 = await orchestrator(
            user_question=user_q2,
            fetch_args=common_fetch_args,
            history=history
        )
        print(f"Assistant: {result2['answer']}\n")
        history = result2["history"]

        # Third user question, leveraging history
        user_q3 = "Summarize everything that was discussed in this conversation."
        print(f"\nUser: {user_q3}\n")
        common_fetch_args["AzureSearchFetcher"]["query"] = user_q3
        result3 = await orchestrator(
            user_question=user_q3,
            fetch_args=common_fetch_args,
            history=history
        )
        print(f"Assistant: {result3['answer']}\n")
        history = result3["history"]

        # Print final metadata and history
        print("==== Metadata from last turn ====")
        for md in result3["metadata"]:
            print(md)
        print("\n==== Full chat history ====")
        for turn in history:
            print(f"{turn['role']}: {turn['content']}")

    asyncio.run(main())
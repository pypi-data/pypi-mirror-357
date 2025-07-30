import asyncio
from typing import Sequence, Dict, Any, List, Optional

from rag_shared.core.fetchers.base import DataFetcher
from rag_shared.core.models.base import LLMModel
from rag_shared.core.prompt_builders.base import PromptBuilder
from rag_shared.utils.config import Config
from rag_shared.core.fetchers.registry import get_processor

class RagOrchestrator:
    def __init__(
        self,
        fetchers: Sequence[DataFetcher],
        model: LLMModel,
        prompt_builder: PromptBuilder,
        config: Config,
        default_proc: str = "default",
        system_prompt: Optional[str] = None
    ):
        self.fetchers       = fetchers
        self.model          = model
        self.prompt_builder = prompt_builder
        self.default_proc   = default_proc
        self.config         = config
        self.system_prompt  = system_prompt or self.config.app.llm.params.system_prompt

    async def __call__(
        self,
        user_question: str,
        fetch_args: Dict[str, Dict[str, Any]] | None = None,
        history: List[Dict[str, str]] | None    = None,
        **model_kwargs: Any
    ) -> Dict[str, Any]:
        fetch_args = fetch_args or {}
        history    = history or []

        # 1 ─ retrieve from all sources concurrently (if any)
        if self.fetchers:
            print("Step 1: Fetching data from all sources...")

            async def _one(fetcher: DataFetcher):
                name = fetcher.__class__.__name__
                args = fetch_args.get(name, {})
                print(f"[RagOrchestrator] Calling {name}.fetch with args: {args}")
                raw = await fetcher.fetch(**args)
                print(f"[RagOrchestrator] Raw {name} returned: {raw}\n")

                # pick processor: override in fetch_args, else YAML default
                proc_name = self.config.app.fetchers.AzureSearchFetcher.processor or self.default_proc
                if not proc_name:
                    raise ValueError(f"No processor specified for {name}.")

                processor_fn = get_processor(name, proc_name)
                processed = processor_fn(raw)
                return name, processed

            # validate fetchers
            if not all(isinstance(f, DataFetcher) for f in self.fetchers):
                raise TypeError("All fetchers must be instances of DataFetcher.")

            print(f"[RagOrchestrator] Fetchers: {[f.__class__.__name__ for f in self.fetchers]}")
            gathered = dict(await asyncio.gather(*[_one(f) for f in self.fetchers]))
        else:
            gathered = {}

        # 2 ─ craft prompt or chat messages
        print("Step 2: Building prompt from fetched data")
        print(f"[RagOrchestrator] Gathered data: {gathered}")
        built = self.prompt_builder.build(gathered, user_question)
        print(f"[RagOrchestrator] Generated prompt/messages:\n{built}\n")

        # 3 ─ LLM call with memory
        print("Step 3: Calling LLM with prompt and history")
        messages: List[Dict[str, str]] = list(history)

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        if isinstance(built, list):
            messages.extend(built)
        else:
            messages.append({"role": "user", "content": built})
        print(f"[RagOrchestrator] Full chat messages:\n{messages}\n")

        response = await self.model.generate(messages=messages, **model_kwargs)
        print(f"[RagOrchestrator] Model response:\n{response}\n")

        # 4 - Extract metadata from AzureSearchFetcher if present
        metadata: List[Dict[str, Any]] = []
        azure = gathered.get("AzureSearchFetcher", {})
        for doc in azure.get("results", []):
            metadata.append({
                "video_url": doc.get("video_url"),
                "timestamp": doc.get("timestamp"),
                "filename":  doc.get("filename")
            })

        # 5 - Build updated history
        new_history = []
        # preserve system prompt in returned history
        if self.system_prompt:
            new_history.append({"role": "system", "content": self.system_prompt})
        new_history.extend(history)
        new_history.append({"role": "user",      "content": built if isinstance(built, str) else ""})
        new_history.append({"role": "assistant", "content": response})

        # 6 - Return answer, metadata, and updated history
        return {
            "answer":   response,
            "metadata": metadata,
            "history":  new_history
        }



if __name__ == "__main__":
    import asyncio
    import os
    from rag_shared.utils.config import Config
    from rag_shared.core.fetchers.azure_search.azure_search import AzureSearchFetcher
    from rag_shared.core.models.azure_openai import AzureOpenAIModel
    from rag_shared.core.prompt_builders.template import TemplatePromptBuilder

    # 1 - Load your config
    cfg = Config()

    # 2 - Instantiate the Azure Search fetcher
    azure_fetcher = AzureSearchFetcher(config=cfg)

    # 3 - Instantiate Model
    llm_model = AzureOpenAIModel(cfg)

    # 4 - Load the default prompt template and create a PromptBuilder
    builder     = TemplatePromptBuilder(cfg)
    # 5 - Build the orchestrator with your fetcher, model, and prompt builder
    orchestrator = RagOrchestrator(
        fetchers       = [azure_fetcher],
        model          = llm_model,
        prompt_builder = builder,
        config= cfg
    )

    # 6 - Define the user question and the fetch_args for AzureSearchFetcher
    user_question = "Who is David?"
    fetch_args = {
        "AzureSearchFetcher": {
            "query": user_question,
            "filter": "",
            "top_k": 5,
            "include_total_count": True,
            "facets": ["speaker,count:5", "topic"],
            "highlight_fields": ["text"],
            "select_fields": [
                "id","filename","block_id","chunk_index","part","speaker",
                "timestamp","tokens","video_url","keyword","topic","text"
            ],
            "vector_search": True
        }
    }

    # 7 - Kick off the orchestration
    async def main():
        print("\n===== ORCHESTRATION DEMO (Real Services) =====\n")
        print(f"User question: {user_question}")
        print(f"Fetch arguments:\n{fetch_args}\n")

        result = await orchestrator(user_question, fetch_args)

        print("===== ORCHESTRATION COMPLETE =====")
        print(f"Final result:\n{result}\n")

    asyncio.run(main())
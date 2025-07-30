import asyncio
from typing import List, Dict, Any, Optional
import openai
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
)
from .base import LLMModel
from rag_shared.utils.config import Config
from rag_shared.resources import load_prompt


class AzureOpenAIModel(LLMModel):
    def __init__(
        self,
        config: Config,
    ):
        """
        :param config: Config instance containing connection info and defaults
        """
        self.config = config

        # --- load system and user prompts from resources via config ---
        llm_params = config.app.llm.params
        folder = llm_params.prompt_folder
        # system prompt template filename
        sys_tpl = llm_params.system_prompt
        # user prompt template filename
        user_tpl = llm_params.prompt

        # raw Jinja templates
        self.system_prompt = load_prompt(template=sys_tpl, prompt_folder=folder)
        self.default_user_prompt = load_prompt(template=user_tpl, prompt_folder=folder)

        # OpenAI client
        self.client = openai.AzureOpenAI(
            api_key          = config.openai_api_key,
            api_version      = config.openai_api_version,
            azure_endpoint   = config.openai_api_base,
            azure_deployment = config.openai_deployment
        )

        # defaults from config
        self.defaults = {
            "max_tokens":        llm_params.default_max_tokens,
            "temperature":       llm_params.default_temperature,
            "top_p":             getattr(llm_params, 'default_top_p', 1.0),
            "frequency_penalty": getattr(llm_params, 'default_frequency_penalty', 0.0),
            "presence_penalty":  getattr(llm_params, 'default_presence_penalty', 0.0)
        }

    async def generate(
        self,
        prompt: Optional[str]            = None,
        messages: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str]     = None,
        **override_kwargs: Any
    ) -> str:
        """
        Generate a chat completion.
        - Uses default_user_prompt if `prompt` is None and `messages` is None.
        """
        # choose system prompt
        sys_text = system_prompt or self.system_prompt

        # build message list
        if messages is None:
            # use direct prompt or fallback to default_user_prompt
            if prompt is None:
                prompt = self.default_user_prompt
            chat_msgs: List[ChatCompletionMessageParam] = [
                ChatCompletionSystemMessageParam(role="system",  content=sys_text),
                ChatCompletionUserMessageParam(  role="user",    content=prompt)
            ]
        else:
            chat_msgs: List[ChatCompletionMessageParam] = [
                ChatCompletionSystemMessageParam(role="system", content=sys_text)
            ]
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content", "")
                if role == "system":
                    chat_msgs.append(ChatCompletionSystemMessageParam(role="system", content=content))
                elif role == "user":
                    chat_msgs.append(ChatCompletionUserMessageParam(role="user", content=content))
                elif role == "assistant":
                    chat_msgs.append(ChatCompletionAssistantMessageParam(role="assistant", content=content))
                else:
                    raise ValueError(f"Unsupported role: {role}")

        # merge defaults and overrides
        params = { **self.defaults, **override_kwargs }

        # call OpenAI
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model    = self.config.openai_deployment,
            messages = chat_msgs,
            **params
        )

        text = response.choices[0].message.content
        return text.strip() if text is not None else ""


if __name__ == "__main__":
    import asyncio
    from rag_shared.utils.config import Config

    cfg = Config()
    model = AzureOpenAIModel(cfg)
    #print the system prompt
    print("System Prompt:", model.system_prompt)
    #print the default user prompt
    print("Default User Prompt:", model.default_user_prompt)
    # Example usage

    async def main():
        resp = await model.generate(prompt="What is the capital of France?")
        print(resp)

    asyncio.run(main())
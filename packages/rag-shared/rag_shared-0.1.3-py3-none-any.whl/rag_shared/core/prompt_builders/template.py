import json
from jinja2 import Template
from typing import Any, Dict, List, Union
from .base import PromptBuilder
from rag_shared.resources import load_prompt
from rag_shared.utils.config import Config

class TemplatePromptBuilder(PromptBuilder):
    def __init__(self, config: Config):
        """
        :param config: Config instance containing prompt_folder and prompt template name under app.llm.params
        """
        llm_params = config.app.llm.params
        folder = llm_params.prompt_folder
        template_name = llm_params.prompt
        # load default prompt template text
        template_str = load_prompt(template=template_name, prompt_folder=folder)
        self.template = Template(template_str)

    def build(
        self,
        fetched: Dict[str, Any],
        user_question: str
    ) -> Union[str, List[Dict[str, str]]]:
        """
        Renders the template with the provided data and question.
        If the rendered output is a JSON array of messages, returns it as a list.
        Otherwise returns the rendered string.
        """
        rendered = self.template.render(data=fetched, question=user_question)
        # attempt to parse as JSON messages
        try:
            obj = json.loads(rendered)
            if isinstance(obj, list):
                return obj
        except json.JSONDecodeError:
            pass
        return rendered
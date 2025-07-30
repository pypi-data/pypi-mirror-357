from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import yaml
import os
import logging

from rag_shared.resources import load_project_config

# ---------------------------
# YAML-config dataclasses
# ---------------------------
@dataclass
class RestAPIParams:
    base_url: str
    token: Optional[str] = None

@dataclass
class RestAPIFetcherConfig:
    processor: str
    params: RestAPIParams

@dataclass
class AzureSearchParams:
    query: str
    filter: str
    top_k: int = 5
    skip: int = 0
    include_total_count: bool = False
    facets: Optional[List[str]] = None
    highlight_fields: Optional[List[str]] = None
    search_fields: Optional[List[str]] = None
    select_fields: Optional[List[str]] = None
    semantic: bool = False
    semantic_config: Optional[str] = None
    vector_search: bool = False
    hybrid: Optional[float] = None
    vector_field: str = "contentVector"

@dataclass
class AzureSearchFetcherConfig:
    processor: str
    params: AzureSearchParams

@dataclass
class FetchersConfig:
    RestAPIFetcher: RestAPIFetcherConfig
    AzureSearchFetcher: AzureSearchFetcherConfig

@dataclass
class LLMParams:
    prompt_folder: str
    system_prompt: str
    prompt: str
    default_max_tokens: int
    default_temperature: float

@dataclass
class LLMConfig:
    type: str
    processor: str
    params: LLMParams

@dataclass
class IndexConfig:
    name: str
    skillset_name: str
    indexer_name: str
    indexes_path: str
    index_yml_path: str
    vector_dim: int = 1536
    vector_field: str = "content_vector"
    index_text_field: str = "text"

@dataclass
class OtherConfig:
    debug: bool
    log_level: str

@dataclass
class AppConfig:
    name: str
    deployment: str
    fetchers: FetchersConfig
    llm: LLMConfig
    index: IndexConfig
    other: OtherConfig

# Singleton metaclass to ensure only one instance of Config exists throughout the application
class SingletonMeta(type):
    _instances: Dict[type, object] = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    def __init__(self,
                 key_vault_name: Optional[str] = None,
                 config_filename: Optional[str] = None,
                 config_dir: Optional[str] = None):
        # prevent re-init in singleton
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        # 1) pick up env vars (or use passed-in values)
        self.key_vault_name = (
            key_vault_name
            or os.getenv("KEY_VAULT_NAME")
        )
        if not self.key_vault_name:
            raise ValueError("KEY_VAULT_NAME must be set")

        raw = load_project_config()
        app_cfg = raw.get("app", {})
        self.app: AppConfig = self._parse_app_config(app_cfg)

        # Initialize Key Vault client
        self.key_vault_name = key_vault_name or os.getenv("KEY_VAULT_NAME")
        self.secret_client = self._initialize_keyvault_client()

        # Retrieve secrets from Key Vault (or env fallback)
        self.search_endpoint: str = self._get_secret("AzureSearchEndpoint")
        self.search_key: str = self._get_secret("AzureSearchAPIKey")
        self.index_name: str = self._get_secret("AzureSearchIndexName")
        self.indexer_name: str = self._get_secret("AzureSearchIndexerName")
        self.search_skillset_name: str = self._get_secret("AzureSearchSkillsetName")
        self.search_embedding_url: str = self._get_secret("AzureSearchEmbeddingURL")
        self.search_embedding_api_key: str = self._get_secret("AzureSearchEmbeddingAPIKey")
        self.search_embedding_dim: int = int(self._get_secret("AzureSearchEmbeddingDim"))
        self.search_embedding_api_version: str = self._get_secret("AzureSearchEmbeddingAPIVersion")
        self.search_embedding_model: str = self._get_secret("AzureSearchEmbeddingModel")
        self.search_deployment_name: str = self._get_secret("AzureSearchDeploymentName")
        self.open_ai_endpoint: str = self._get_secret("OpenAIEndpoint")
        self.open_ai_key: str = self._get_secret("OpenAIModelAPIKey")
        self.openai_api_type: str = self._get_secret("OpenAIAPIType")
        self.openai_api_base: str = self._get_secret("OpenAIAPIBaseURL")
        self.openai_api_key: str = self._get_secret("OpenAIAPIKey")
        self.openai_api_version: str = self._get_secret("OpenAIAPIVersion")
        self.openai_model_name: str = self._get_secret("OpenAIModelName")
        self.openai_deployment: str = self._get_secret("OpenAIDeployment")
        self.index_text_field: str = self._get_secret("IndexTextField")
        self.index_content_vector_field: str = self._get_secret("IndexContentVectorField")

    def _parse_app_config(self, cfg: dict) -> AppConfig:
        """Convert raw dict to AppConfig dataclass."""
        rest_params = RestAPIParams(**cfg["fetchers"]["RestAPIFetcher"]["params"])
        rest_fetcher = RestAPIFetcherConfig(
            processor=cfg["fetchers"]["RestAPIFetcher"]["processor"],
            params=rest_params
        )
        azure_search_params = AzureSearchParams(**cfg["fetchers"]["AzureSearchFetcher"]["params"])
        azure_search_fetcher = AzureSearchFetcherConfig(
            processor=cfg["fetchers"]["AzureSearchFetcher"]["processor"],
            params=azure_search_params
        )


        fetchers = FetchersConfig(RestAPIFetcher=rest_fetcher, AzureSearchFetcher=azure_search_fetcher)

        llm_params = LLMParams(**cfg["llm"]["params"])
        llm = LLMConfig(
            type=cfg["llm"]["type"],
            processor=cfg["llm"]["processor"],
            params=llm_params
        )

        index = IndexConfig(**cfg.get("index", {}))
        other = OtherConfig(**cfg.get("other", {}))
        return AppConfig(
            name=cfg.get("name", ""),
            deployment=cfg.get("deployment", ""),
            fetchers=fetchers,
            llm=llm,
            index=index,
            other=other
        )

    def _initialize_keyvault_client(self) -> SecretClient:
        """Initialize Azure Key Vault client with DefaultAzureCredential"""
        if not self.key_vault_name:
            raise ValueError("Key Vault name must be provided")
        vault_uri = f"https://{self.key_vault_name}.vault.azure.net"
        credential = DefaultAzureCredential()
        return SecretClient(vault_url=vault_uri, credential=credential)

    def _get_secret(self, name: str) -> str:
        """Retrieve secret from Key Vault, fallback to env var."""
        try:
            sec = self.secret_client.get_secret(name)
            return sec.value or ""
        except Exception:
            env_name = name.upper().replace('-', '_')
            val = os.getenv(env_name)
            if val is not None:
                logging.warning(f"Falling back to env var for {name}")
                return val
            raise

    def _load_yaml(self, path: str) -> dict:
        """Load YAML file into dict."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logging.warning(f"YAML config not found at {path}, using empty config.")
            return {}
        except Exception as e:
            logging.error(f"Error loading YAML config: {e}")
            return {}
        
    # ----------------------------------------------------------------
    # Pretty‐print and serialization
    # ----------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the entire config (app + vault‐backed secrets) into a plain dict.
        """
        from dataclasses import asdict

        data: Dict[str, Any] = {}
        # 1) the YAML‐driven app config
        data["app"] = asdict(self.app)

        # 2) vault‐backed endpoints & keys
        for attr in (
            "search_endpoint", "search_key", "index_name",
            "indexer_name", "search_skillset_name",
            "search_embedding_url", "search_embedding_api_key",
            "search_embedding_dim", "search_embedding_api_version",
            "search_embedding_model", "search_deployment_name",
            "open_ai_endpoint", "open_ai_key", "openai_api_type",
            "openai_api_base", "openai_api_key", "openai_api_version",
            "openai_model_name", "openai_deployment",
            "index_text_field", "index_content_vector_field"
        ):
            if hasattr(self, attr):
                data[attr] = getattr(self, attr)

        return data

    def __repr__(self) -> str:
        # for interactive shells
        return self.__str__()

    def __str__(self) -> str:
        # pretty‐print as JSON
        import json
        return json.dumps(self.to_dict(), indent=2)


if __name__ == "__main__":

    # Set temp environment variables for testing
    KEY_VAULT_NAME = os.getenv("KEY_VAULT_NAME", "RecoveredSpacesKV")
    CONFIG_PATH    = os.getenv("CONFIG_PATH",    "configs")
    CONFIG_FILE    = os.getenv("CONFIG_FILE",    "recovered_config.yml")

    # Instantiate (will only ever create one instance)
    config = Config()
    print("Configuration loaded successfully.\n")

    # ————————————————————————————————————————————————
    # Vault‑backed secrets
    # ————————————————————————————————————————————————
    print("Azure Search Endpoint:    ", config.search_endpoint)
    print("Azure Search API Key:     ", config.search_key)
    print("Azure Search Index Name:  ", config.index_name)
    print("OpenAI Endpoint:          ", config.open_ai_endpoint)
    print("OpenAI API Key:           ", config.open_ai_key, "\n")

    # ————————————————————————————————————————————————
    # YAML‑driven app settings
    # ————————————————————————————————————————————————
    app_cfg = config.app
    print("--- App Settings (from YAML) ---")
    print(f"App Name:         {app_cfg.name}")
    print(f"Deployment Slot:  {app_cfg.deployment}\n")

    # Fetchers
    rest_cfg = app_cfg.fetchers.RestAPIFetcher
    print("Fetcher: RestAPIFetcher")
    print("  Processor:      ", rest_cfg.processor)
    print("  Base URL:       ", rest_cfg.params.base_url)
    print("  Token:          ", rest_cfg.params.token, "\n")

    azure_search_cfg = app_cfg.fetchers.AzureSearchFetcher
    print("Fetcher: AzureSearchFetcher")
    print("  Processor:      ", azure_search_cfg.processor)
    print("  Query:          ", azure_search_cfg.params.query)
    print("  Filter:         ", azure_search_cfg.params.filter)
    print("  Top K:          ", azure_search_cfg.params.top_k)
    print("  Include total:  ", azure_search_cfg.params.include_total_count)
    print("  Facets:         ", azure_search_cfg.params.facets)
    print("  Highlight fields:", azure_search_cfg.params.highlight_fields)
    print("  Search fields:  ", azure_search_cfg.params.search_fields)
    print("  Select fields:  ", azure_search_cfg.params.select_fields)
    print("  Semantic:       ", azure_search_cfg.params.semantic)
    print("  Semantic config:", azure_search_cfg.params.semantic_config)
    print("  Vector search:  ", azure_search_cfg.params.vector_search)
    print("  Hybrid:         ", azure_search_cfg.params.hybrid)
    print("  Vector field:   ", azure_search_cfg.params.vector_field, "\n")

    # LLM
    llm = app_cfg.llm
    print("LLM:")
    print("  Type:               ", llm.type)
    print("  Processor:          ", llm.processor)
    print("  Prompt folder:      ", llm.params.prompt_folder)
    print("  System prompt file: ", llm.params.system_prompt)
    print("  User prompt file:   ", llm.params.prompt)
    print("  Max tokens:         ", llm.params.default_max_tokens)
    print("  Temperature:        ", llm.params.default_temperature, "\n")

    # Index
    idx = app_cfg.index
    print("Index:")
    print("  Name:         ", idx.name)
    print("  Skillset:     ", idx.skillset_name)
    print("  Indexer:      ", idx.indexer_name, "\n")
    print("  Index YAML:   ", idx.index_yml_path, "\n")
    print("  Vector dim:   ", idx.vector_dim)
    print("  Vector field: ", idx.vector_field)
    print("  Text field:   ", idx.index_text_field, "\n")
    

    # Other
    other = app_cfg.other
    print("Other:")
    print("  Debug:        ", other.debug)
    print("  Log level:    ", other.log_level, "\n")

    # ————————————————————————————————————————————————
    # Verify singleton behavior
    # ————————————————————————————————————————————————
    second = Config()
    assert config is second, "Config should be a singleton!"
    print("Singleton verified: config is the same instance on second call.")
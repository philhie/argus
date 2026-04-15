"""Configuration via environment variables and .env file."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys (optional — modules that need them skip gracefully)
    shodan_api_key: str = ""
    hibp_api_key: str = ""
    github_token: str = ""
    serpapi_key: str = ""
    anthropic_api_key: str = ""

    # Scanner defaults
    output_dir: str = "results"
    max_concurrent_requests: int = 10
    request_timeout: int = 10

    # DNS
    dns_resolver: str = "8.8.8.8"

    # Module toggles (legal sensitivity)
    enable_axfr: bool = True  # Zone transfer test — set False if concerned about legality
    enable_ntlm: bool = True  # NTLM challenge — set False to skip AD domain extraction

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

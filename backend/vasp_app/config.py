from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_prefix="ATLAS_", extra="ignore")
    data_dir: Path = ROOT / ".local"
    database_url: str = ""
    secure_cookie: bool = False
    session_hours: int = 8
    etherscan_api_key: str = ""
    etherscan_metadata_enabled: bool = False
    cctp_enabled: bool = False
    trongrid_api_key: str = ""
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    bitcoin_api_url: str = "https://mempool.space/api"
    bitcoin_provider: Literal["esplora", "blockcypher"] = "esplora"
    blockcypher_api_url: str = "https://api.blockcypher.com/v1/btc/main"
    provider_timeout: float = 15.0
    local_bootstrap: bool = True
    worker_enabled: bool = True
    allowed_origins: str = (
        "http://127.0.0.1:8787,http://localhost:8787,http://127.0.0.1:5173,http://localhost:5173"
    )
    max_body_bytes: int = 10_000_000
    allowed_hosts: str = "127.0.0.1,localhost,testserver"

    @model_validator(mode="after")
    def default_database(self):
        if not self.database_url:
            self.database_url = f"sqlite:///{self.data_dir / 'atlas.sqlite3'}"
        return self


settings = Settings()

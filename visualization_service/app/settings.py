from pydantic_settings import BaseSettings

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    auth_host: str
    auth_port: str

    redis_host: str
    redis_port: str

    temp_dir: str = "temp"

    def get_url(self, host: str, port: str):
        return "http://{host}:{port}".format(
            host=host,
            port=port,
        )

    @property
    def auth_url(self) -> str:
        return self.get_url(self.auth_host, self.auth_port)


settings = Settings()

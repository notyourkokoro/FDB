from pydantic_settings import BaseSettings

from dotenv import load_dotenv
from pathlib import Path

# Загрузка переменных окружения
load_dotenv()


BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """
    Класс-хранилище переменных окружения
    """

    postgres_name: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    echo: bool = False

    storage_dir: str

    auth_host: str
    auth_port: str

    @property
    def db_url(self) -> str:
        """
        Получение строки подключения к базе данных
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}".format(
            user=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            name=self.postgres_name,
        )

    @property
    def auth_url(self) -> str:
        """
        Получение адреса сервиса авторизации
        """
        return "http://{host}:{port}".format(
            host=self.auth_host,
            port=self.auth_port,
        )


# Получение переменных окружения
settings = Settings()

from pydantic_settings import BaseSettings

from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


class Settings(BaseSettings):
    """
    Настройки приложения
    (хранилище переменных окружения)
    """

    postgres_name: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    echo: bool = False

    @property
    def db_url(self) -> str:
        """Получение строки подключения к базе данных"""

        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}".format(
            user=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            name=self.postgres_name,
        )


# Получение переменных окружения
settings = Settings()

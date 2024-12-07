from pydantic_settings import BaseSettings

from dotenv import load_dotenv
from pathlib import Path

# Загрузка переменных окружения
load_dotenv()

# Путь к корню сервиса
BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """
    Класс-хранилище переменных окружения
    """

    auth_host: str
    auth_port: str

    redis_host: str
    redis_port: str

    temp_dir: str = "temp"

    def get_url(self, host: str, port: str):
        """
        Получение адреса сервиса

        Parameters
        ----------
        host : str
            Хост
        port : str
            Порт
        """
        return "http://{host}:{port}".format(
            host=host,
            port=port,
        )

    @property
    def auth_url(self) -> str:
        """
        Получение адреса сервиса авторизации
        """
        return self.get_url(self.auth_host, self.auth_port)


# Получение переменных окружения
settings = Settings()

from pydantic_settings import BaseSettings

from dotenv import load_dotenv
from pathlib import Path

# Загрузка переменных окружения из файла .env
load_dotenv()

# Путь к корню сервиса
BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """
    Класс для хранения переменных окружения и
    предоставления доступа к ним
    """

    auth_host: str
    auth_port: str

    storage_host: str
    storage_port: str

    redis_host: str
    redis_port: str

    # Директория по умолчанию для временных файлов
    temp_dir: str = "temp"

    def get_url(self, host: str, port: str):
        """
        Формирует URL на основе хоста и порта

        Parameters
        ----------
        host : str
            Хост, к которому нужно сформировать URL
        port : str
            Порт для формирования URL

        Returns
        -------
        str
            Сформированный URL
        """
        return "http://{host}:{port}".format(
            host=host,
            port=port,
        )

    @property
    def auth_url(self) -> str:
        """
        Формирует и возвращает URL для
        отправки запросов в сервис авторизации

        Returns
        -------
        str
            URL для отравки запросов в сервис авторизации
        """
        return self.get_url(self.auth_host, self.auth_port)

    @property
    def storage_url(self) -> str:
        """
        Формирует и возвращает URL отправки
        запросовв в сервис для хранения файлов

        Returns
        -------
        str
            URL для отравки запросов в сервис для хранения файлов
        """
        return self.get_url(self.storage_host, self.storage_port)


# Получение переменных окружения в виде
# объекта класса Settings
settings = Settings()

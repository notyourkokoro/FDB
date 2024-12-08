import httpx
import pandas as pd

from io import BytesIO

from app.settings import settings
from app.exceptions import MirrorHTTPException, ServerException
from app.schemas import DataFormat, DataMediaType
from app.utils import TempStorage
from app.data.exceptions import LoadCSVException, CSVSepException


class StorageServiceRequests:
    """
    Класс для работы с запросами к сервису хранения файлов
    """

    @staticmethod
    async def get_user_file(
        user_token: str, file_id: int, sep: str | None = None
    ) -> pd.DataFrame:
        """
        Получение файла пользователя по
        его токену и идентификатору файла

        Parameters
        ----------
        user_token : str
            Токен пользователя для аутентификации
        file_id : int
            Идентификатор файла, который нужно загрузить в Redis
        sep : str | None
            Разделитель для CSV-файла, если файл в формате CSV

        Returns
        -------
        pd.DataFrame
            Загруженные данные в виде DataFrame,
            которые после будут помещены в Redis

        Raises
        ------
        MirrorHTTPException
            Если статус ответа от сервиса не равен 200
        CSVSepException
            Если разделитель не указан при загрузке CSV
        LoadCSVException
            Если произошла ошибка при загрузке CSV
        """
        # Отправка запроса для получения файла
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.storage_url}/storage/download/{file_id}",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        if response.status_code != 200:
            raise MirrorHTTPException(response)

        # Создание объекта BytesIO для чтения содержимого ответа
        response_content = response.content
        file_obj = BytesIO(response_content)

        # Определение формата файла (Excel или CSV)
        # с последующим его чтением в DataFrame
        if response_content.startswith(b"PK\x03\x04") or response_content.startswith(
            b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
        ):
            df = pd.read_excel(file_obj)
        else:
            if sep is None:
                raise CSVSepException
            try:
                df = pd.read_csv(file_obj, sep=sep)
            except Exception:
                raise LoadCSVException

        return df

    @staticmethod
    async def sent_file(
        user_token: str, file_id: int, file_obj: BytesIO, filetype: DataFormat
    ) -> dict:
        """
        Отправка файла в сервис для
        хранения пользовательских файлов

        Parameters
        ----------
        user_token : str
            Токен пользователя для аутентификации
        file_id : int
            Идентификатор файла, к которому
            будет привязан новый файл
        file_obj : BytesIO
            Объект файла в формате BytesIO
        filetype : DataFormat
            Формат файла (например, CSV, XLSX)

        Returns
        -------
        dict
            Ответ от сервиса в виде словаря

        Raises
        ------
        ServerException
            Если произошла ошибка при обращении к серверу
        MirrorHTTPException
            Если статус ответа от сервиса не равен 201
        """
        try:
            async with httpx.AsyncClient() as client:
                # Генерация имени файла и типа файла
                media_type = getattr(DataMediaType, filetype.name).value
                filename = TempStorage.get_name(filetype=filetype)

                # Отправка файла на сервер
                response = await client.post(
                    f"{settings.storage_url}/storage/add/version",
                    headers={"Authorization": f"Bearer {user_token}"},
                    params={"based_file_id": file_id},
                    files={
                        "upload_file_obj": (
                            filename,
                            file_obj,
                            media_type,
                        )
                    },
                )
        except Exception:
            raise ServerException

        if response.status_code != 201:
            raise MirrorHTTPException(response)

        return response.json()

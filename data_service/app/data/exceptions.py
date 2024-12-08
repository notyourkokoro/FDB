from fastapi import status
from fastapi.exceptions import HTTPException


class ColumnsExistsException(HTTPException):
    """
    Исключение, выбрасываемое, когда колонки
    с указанными именами уже существуют
    (допустим, при попытке создать колонку с таким же именем)
    """

    def __init__(self, columns: list[str]):
        """
        Инициализация исключения

        Parameters
        ----------
        columns : list[str]
            Список названий колонок, которые
            уже существуют с такими именами
        """
        detail = f"Колонки с такими именами уже существуют: {', '.join(columns)}!"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# Исключение для случая, когда данные
# не были загружены пользователем в Redis
DataNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Для начала необходимо загрузить данные!",
)


# Исключение для случая некорректного выражения
EvalException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Некорректное выражение!",
)


# Исключение для случая некорректного сопоставления типов данных в выражении
EvalTypeException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Некорректное сопоставление типов данных в выражении!",
)


# Исключение для случая, когда разделитель CSV-файла не указан
CSVSepException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="При загрузке CSV-файла должен быть обязательно указан разделитель!",
)


# Исключение для случая ошибки при загрузке CSV-файла с неверным разделителем
LoadCSVException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Ошибка при загрузке CSV-файла. Вероятно, неверно указан разделитель",
)


# Исключение для случая некорректного сопоставления
# типов данных в колонках при объединении
MergeColumnsTypeException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Некорректное сопоставление типов данных в колонках!",
)

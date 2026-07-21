class ShortIDGenerationError(Exception):
    """Исключение при невозможности сгенерировать уникальный идентификатор"""
    pass


class FileUploadError(Exception):
    """Исключение при ошибке загрузки файла"""
    pass
import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    YANDEX_API_HOST = 'https://cloud-api.yandex.net/'
    YANDEX_API_VERSION = 'v1'
    YANDEX_BASE_URL = f'{YANDEX_API_HOST}{YANDEX_API_VERSION}/disk/resources'
    YANDEX_UPLOAD_URL = f'{YANDEX_BASE_URL}/upload'
    YANDEX_DOWNLOAD_URL = f'{YANDEX_BASE_URL}/download'
    YANDEX_RESOURCES_URL = YANDEX_BASE_URL
    YANDEX_APP_PREFIX = 'app:'
    YANDEX_APP_FOLDER = '/yacut_uploads'
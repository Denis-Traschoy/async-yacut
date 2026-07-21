import random
import string

import aiohttp

from yacut.constants import SHORT_ID_LENGTH
from yacut.exceptions import FileUploadError, ShortIDGenerationError
from yacut.models import URLMap

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
REQUEST_DOWNLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'
REQUEST_RESOURCES_URL = f'{API_HOST}{API_VERSION}/disk/resources'
APP_PREFIX = 'app:'
APP_FOLDER = '/yacut_uploads'


def generate_short_id():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(SHORT_ID_LENGTH))


def get_unique_short_id(max_attempts=1000):
    for _ in range(max_attempts):
        short_id = generate_short_id()
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    raise ShortIDGenerationError(
        f'Не удалось сгенерировать уникальный короткий идентификатор '
        f'за {max_attempts} попыток'
    )


def normalize_url(url):
    if not url:
        return url
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def build_short_link(short_id, base_url):
    if not base_url.endswith('/'):
        base_url += '/'
    return f'{base_url}{short_id}'


async def ensure_folder(session, headers):
    async with session.get(
        REQUEST_RESOURCES_URL,
        headers=headers,
        params={'path': APP_FOLDER},
    ) as response:
        if response.status == 404:
            async with session.put(
                REQUEST_RESOURCES_URL,
                headers=headers,
                params={'path': APP_FOLDER},
            ):
                pass


async def upload_to_yandex_disk(file, token):
    headers = {'Authorization': f'OAuth {token}'}
    filename = file.filename
    remote_path = f'{APP_PREFIX}{APP_FOLDER}/{filename}'
    async with aiohttp.ClientSession() as session:
        await ensure_folder(session, headers)
        payload = {'path': remote_path, 'overwrite': 'false'}
        async with session.get(
            REQUEST_UPLOAD_URL,
            headers=headers,
            params=payload,
        ) as response:
            if response.status != 200:
                raise FileUploadError(
                    'Не удалось получить ссылку для загрузки'
                )
            data = await response.json()
            upload_url = data.get('href')
            if not upload_url:
                raise FileUploadError(
                    'Не удалось получить ссылку для загрузки'
                )
        file.seek(0)
        async with session.put(upload_url, data=file.read()) as response:
            if response.status not in (201, 202):
                raise FileUploadError(
                    'Не удалось загрузить файл на Яндекс.Диск'
                )
        async with session.get(
            REQUEST_DOWNLOAD_URL,
            headers=headers,
            params={'path': remote_path},
        ) as response:
            if response.status != 200:
                raise FileUploadError(
                    'Не удалось получить ссылку для скачивания'
                )
            data = await response.json()
            download_url = data.get('href')
            if not download_url:
                raise FileUploadError(
                    'Не удалось получить ссылку для скачивания'
                )
            return download_url
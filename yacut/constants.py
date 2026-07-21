import re

# Если суть мэджик намбер в том чтобы константы было видно, то по идее
# можно вынести дальше, в отдельный файл, так можно будет перешивать
# все константы проекта здесь
SHORT_ID_LENGTH = 6
SHORT_ID_MIN_LENGTH = 1
SHORT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9]{1,16}$')
RESERVED_PATHS = ['files', 'api', 'admin', 'static']
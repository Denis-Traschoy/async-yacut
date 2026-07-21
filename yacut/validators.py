import validators as url_validators
from wtforms.validators import ValidationError

from yacut.constants import RESERVED_PATHS, SHORT_ID_LENGTH, SHORT_ID_PATTERN
from yacut.models import URLMap


def validate_url(url):
    return bool(url and url_validators.url(url))


def validate_short_id(short_id):
    return bool(
        short_id
        and len(short_id) <= SHORT_ID_LENGTH
        and SHORT_ID_PATTERN.match(short_id)
    )


def is_reserved_path(path):
    if not path:
        return False
    path_lower = path.lower()
    for reserved in RESERVED_PATHS:
        if path_lower == reserved or path_lower.startswith(f'{reserved}/'):
            return True
    return False


def validate_custom_id(custom_id):
    if not custom_id:
        return None
    errors = []
    if not validate_short_id(custom_id):
        errors.append('Указано недопустимое имя для короткой ссылки')
    if is_reserved_path(custom_id):
        errors.append('Указано недопустимое имя для короткой ссылки')
    return errors if errors else []


def validate_original_link(form, field):
    if not validate_url(field.data):
        raise ValidationError('Указан недопустимый URL')


def validate_custom_id_form(form, field):
    if not field.data:
        return
    if not validate_short_id(field.data):
        raise ValidationError(
            'Указано недопустимое имя для короткой ссылки'
        )
    if is_reserved_path(field.data):
        raise ValidationError(
            'Предложенный вариант короткой ссылки уже существует.'
        )
    if URLMap.query.filter_by(short=field.data).first():
        raise ValidationError(
            'Предложенный вариант короткой ссылки уже существует.'
        )
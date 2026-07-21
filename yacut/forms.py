from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from yacut.constants import SHORT_ID_LENGTH, SHORT_ID_MIN_LENGTH
from yacut.validators import validate_custom_id_form, validate_original_link


class URLMapForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='URL не может быть пустым'),
            validate_original_link,
        ]
    )
    custom_id = StringField(
        'Короткая ссылка',
        validators=[
            Optional(),
            Length(
                min=SHORT_ID_MIN_LENGTH,
                max=SHORT_ID_LENGTH,
                message=(
                    f'Короткая ссылка должна быть '
                    f'от {SHORT_ID_MIN_LENGTH} до {SHORT_ID_LENGTH} символов'
                ),
            ),
            validate_custom_id_form,
        ]
    )
    submit = SubmitField('Сократить')


class FileUploadForm(FlaskForm):
    files = MultipleFileField(
        'Файлы',
        validators=[
            FileRequired(message='Файл не выбран'),
        ]
    )
    submit = SubmitField('Загрузить')
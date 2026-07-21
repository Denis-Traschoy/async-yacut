import os

from flask import Blueprint, flash, redirect, render_template, request
from markupsafe import Markup

from yacut.exceptions import FileUploadError, ShortIDGenerationError
from yacut.forms import FileUploadForm, URLMapForm
from yacut.models import URLMap, db
from yacut.utils import (
    build_short_link,
    get_unique_short_id,
    normalize_url,
    upload_to_yandex_disk,
)
from yacut.validators import is_reserved_path

views_bp = Blueprint('views', __name__)


@views_bp.route('/', methods=['GET', 'POST'])
def index():
    form = URLMapForm()
    if form.validate_on_submit():
        original_url = normalize_url(form.original_link.data)
        custom_id = form.custom_id.data
        if custom_id:
            short_id = custom_id
        else:
            try:
                short_id = get_unique_short_id()
            except ShortIDGenerationError:
                flash(
                    'Не удалось создать короткую ссылку. Попробуйте позже.',
                    'error'
                )
                return render_template('index.html', form=form)
        url_map = URLMap(original=original_url, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        base_url = request.host_url.rstrip('/')
        short_link = build_short_link(short_id, base_url)
        flash(
            Markup(
                f'Короткая ссылка создана: '
                f'<a href="{short_link}">{short_link}</a>'
            ),
            'success',
        )
        return render_template('index.html', form=form, short_link=short_link)
    return render_template('index.html', form=form)


@views_bp.route('/<short_id>')
def redirect_to_original(short_id):
    if is_reserved_path(short_id):
        return render_template('404.html'), 404
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return render_template('404.html'), 404
    return redirect(url_map.original)


@views_bp.route('/files', methods=['GET', 'POST'])
async def upload_file():
    form = FileUploadForm()
    if form.validate_on_submit():
        token = os.getenv('DISK_TOKEN')
        if not token:
            flash('Токен Яндекс.Диска не настроен', 'error')
            return render_template('upload.html', form=form)
        files = request.files.getlist('files')
        if not files or not files[0].filename:
            flash('Файл не выбран', 'error')
            return render_template('upload.html', form=form)
        short_links = []
        for file in files:
            if not file.filename:
                continue
            try:
                download_url = await upload_to_yandex_disk(file, token)
            except FileUploadError:
                flash(f'Не удалось загрузить файл {file.filename}', 'error')
                continue
            try:
                short_id = get_unique_short_id()
            except ShortIDGenerationError:
                flash(
                    f'Не удалось создать короткую ссылку для {file.filename}',
                    'error'
                )
                continue
            url_map = URLMap(original=download_url, short=short_id)
            db.session.add(url_map)
            base_url = request.host_url.rstrip('/')
            short_link = build_short_link(short_id, base_url)
            short_links.append((file.filename, short_link))
        db.session.commit()
        _flash_upload_results(short_links)
        return render_template(
            'upload.html',
            form=form,
            short_links=short_links
        )
    return render_template('upload.html', form=form)


def _flash_upload_results(short_links):
    if short_links:
        for filename, link in short_links:
            flash(
                Markup(f'{filename}: <a href="{link}">{link}</a>'),
                'success',
            )
    else:
        flash('Ни один файл не загружен', 'error')


@views_bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
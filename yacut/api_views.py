from http import HTTPStatus

from flask import Blueprint, jsonify, request

from yacut.models import URLMap, db
from yacut.utils import (ShortIDGenerationError, build_short_link,
                         get_unique_short_id, normalize_url)
from yacut.validators import is_reserved_path, validate_custom_id, validate_url

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(
            {'message': 'Отсутствует тело запроса'}
        ), HTTPStatus.BAD_REQUEST
    if 'url' not in data:
        return jsonify(
            {'message': '"url" является обязательным полем!'}
        ), HTTPStatus.BAD_REQUEST
    original_url = normalize_url(data['url'])
    if not validate_url(original_url):
        return jsonify(
            {'message': 'Указан недопустимый URL'}
        ), HTTPStatus.BAD_REQUEST
    custom_id = data.get('custom_id', '')
    if custom_id:
        errors = validate_custom_id(custom_id)
        if errors:
            return jsonify({'message': errors[0]}), HTTPStatus.BAD_REQUEST
        if URLMap.query.filter_by(short=custom_id).first():
            return jsonify({
                'message':
                'Предложенный вариант короткой ссылки уже существует.'
            }), HTTPStatus.BAD_REQUEST
        short_id = custom_id
    else:
        try:
            short_id = get_unique_short_id()
        except ShortIDGenerationError:
            return jsonify({
                'message':
                'Не удалось создать короткую ссылку. Попробуйте позже.'
            }), HTTPStatus.INTERNAL_SERVER_ERROR
    url_map = URLMap(original=original_url, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    base_url = request.host_url.rstrip('/')
    short_link = build_short_link(short_id, base_url)
    return jsonify({
        'url': original_url,
        'short_link': short_link
    }), HTTPStatus.CREATED


@api_bp.route('/id/<short_id>/', methods=['GET'])
def get_original_url(short_id):
    if is_reserved_path(short_id):
        return jsonify(
            {'message': 'Указанный id не найден'}
        ), HTTPStatus.NOT_FOUND
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify(
            {'message': 'Указанный id не найден'}
        ), HTTPStatus.NOT_FOUND
    return jsonify({'url': url_map.original}), HTTPStatus.OK
from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.models import Release, Platform
from app import db

bp = Blueprint('releases', __name__, url_prefix='/api/releases')

@bp.route('/', methods=['POST'])
@login_required
def add_release():
    data = request.get_json()
    release = Release(
        platform_id=data['platform_id'],
        release_type=data['release_type'],
        is_successful=data['is_successful'],
        version=data['version'],
    )
    db.session.add(release)
    db.session.commit()
    return jsonify({'message': 'Release added'}), 201

@bp.route('/', methods=['GET'])
def get_releases():
    releases = Release.query.all()
    result = [{
        'id': r.id,
        'platform_id': r.platform_id,
        'version': r.version,
        'success': r.is_successful
    } for r in releases]
    return jsonify(result)

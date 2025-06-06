from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from app.models import Release
from app import db
from functools import wraps

bp = Blueprint('releases', __name__, url_prefix='/api/releases')

def write_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'writer']:
            return jsonify({'error': 'Write privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/', methods=['POST'])
@login_required
@write_required
def add_release():
    data = request.get_json()
    release = Release(
        platform=data['platform'],
        release_type=data['release_type'],
        is_successful=data['is_successful'],
        version=data['version'],
        mcm_link=data.get('mcm_link'),
        ci_job_link=data.get('ci_job_link'),
        commit_list_link=data.get('commit_list_link')
    )
    db.session.add(release)
    db.session.commit()
    return jsonify({'message': 'Release added'}), 201

@bp.route('/', methods=['GET'])
@login_required
def get_releases():
    platform = request.args.get('platform', type=str)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Release.query
    
    if platform:
        query = query.filter_by(platform=platform)
    if start_date:
        query = query.filter(Release.rollout_date >= start_date)
    if end_date:
        query = query.filter(Release.rollout_date <= end_date)
        
    releases = query.all()
    result = [r.to_dict() for r in releases]
    return jsonify(result)

@bp.route('/<int:release_id>', methods=['PUT'])
@login_required
@write_required
def update_release(release_id):
    release = db.session.get(Release, release_id)
    if not release:
        abort(404)
    data = request.get_json()

    if 'platform' in data:
        release.platform = data['platform']
    if 'release_type' in data:
        release.release_type = data['release_type']
    if 'is_successful' in data:
        release.is_successful = data['is_successful']
    if 'version' in data:
        release.version = data['version']
    if 'mcm_link' in data:
        release.mcm_link = data['mcm_link']
    if 'ci_job_link' in data:
        release.ci_job_link = data['ci_job_link']
    if 'commit_list_link' in data:
        release.commit_list_link = data['commit_list_link']

    db.session.commit()
    return jsonify({'message': 'Release updated successfully'})

@bp.route('/<int:release_id>', methods=['DELETE'])
@login_required
@write_required
def delete_release(release_id):
    release = db.session.get(Release, release_id)
    if not release:
        abort(404)
    db.session.delete(release)
    db.session.commit()
    return jsonify({'message': 'Release deleted successfully'})

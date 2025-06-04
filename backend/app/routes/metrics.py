from flask import Blueprint, request, jsonify
from app.models import Release
from datetime import datetime

bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')

@bp.route('/', methods=['GET'])
def calculate_metrics():
    releases = Release.query.order_by(Release.rollout_date).all()
    if len(releases) < 2:
        return jsonify({'error': 'Not enough data'}), 400

    diffs = [(releases[i+1].rollout_date - releases[i].rollout_date).total_seconds() / 3600
             for i in range(len(releases)-1)]
    avg_hours = sum(diffs) / len(diffs)
    return jsonify({'deployment_frequency': round(24 / avg_hours, 2)})

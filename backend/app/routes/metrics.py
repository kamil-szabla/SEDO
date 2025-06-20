from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.models import Release, Incident
from datetime import datetime
from app.utils import (
    calculate_deployment_frequency,
    calculate_lead_time,
    calculate_change_failure_rate,
    calculate_time_to_restore,
    get_filtered_releases,
    get_filtered_incidents
)

bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')

def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str) if date_str else None
    except ValueError:
        return None

@bp.route('/', methods=['GET'])
@login_required
def calculate_metrics():
    platform = request.args.get('platform', type=str)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    start = parse_date(start_date)
    end = parse_date(end_date)

    if (start_date and not start) or (end_date and not end):
        return jsonify({'error': 'Invalid date format, expected ISO-8601'}), 400

    releases = get_filtered_releases(platform, start_date, end_date)
    if not releases:
        return jsonify({
            "deployment_frequency": { "value": 0, "trend": 0, "history": [] },
            "lead_time": { "value": 0, "trend": 0, "history": [] },
            "change_failure_rate": { "value": 0, "trend": 0, "history": [] },
            "time_to_restore": { "value": 0, "trend": 0, "history": [] },
            "note": "No releases found for the given criteria"
        }), 200

    release_ids = [r.id for r in releases]
    incidents = get_filtered_incidents(release_ids, start_date, end_date)

    metrics = {
        'deployment_frequency': calculate_deployment_frequency(releases, start, end),
        'lead_time': calculate_lead_time(releases),
        'change_failure_rate': calculate_change_failure_rate(releases),
        'time_to_restore': calculate_time_to_restore(incidents)
    }

    return jsonify(metrics)

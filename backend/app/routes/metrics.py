from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import db
from app.models import Release, Incident
from datetime import datetime
from app.utils import (
    calculate_change_failure_rate_trend,
    calculate_deployment_frequency,
    calculate_deployment_frequency_trend,
    calculate_lead_time,
    calculate_change_failure_rate,
    calculate_lead_time_trend,
    calculate_time_to_restore,
    calculate_time_to_restore_trend,
    get_filtered_releases,
    get_filtered_incidents,
    get_previous_period_dates
)

bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')

def parse_date(date_str):
    """Parse date string to datetime object (not date object)"""
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

    # Calculate current period metrics
    current_releases = [r for r in releases if 
                       (not start or datetime.combine(r.rollout_date, datetime.min.time()) >= start) and
                       (not end or datetime.combine(r.rollout_date, datetime.min.time()) <= end)]
    current_release_ids = [r.id for r in current_releases]
    current_incidents = [i for i in incidents if 
                    i.release_id in current_release_ids and
                    (not start or i.start_time >= start) and
                    (not end or i.end_time <= end)]

    # Calculate previous period metrics
    if start and end:
        prev_start, prev_end = get_previous_period_dates(start, end)
        prev_releases = [r for r in releases if 
                        datetime.combine(r.rollout_date, datetime.min.time()) >= prev_start and
                        datetime.combine(r.rollout_date, datetime.min.time()) <= prev_end]
        prev_release_ids = [r.id for r in prev_releases]
        prev_incidents = [i for i in incidents if i.release_id in prev_release_ids]
    else:
        prev_releases = []
        prev_incidents = []

    metrics = {
        'deployment_frequency': {
            'value': calculate_deployment_frequency(current_releases, start, end),
            'trend': calculate_deployment_frequency_trend(current_releases, start, end) if start and end else 0,
            'history': []
        },
        'lead_time': {
            'value': calculate_lead_time(current_releases),
            'trend': calculate_lead_time_trend(current_releases, prev_releases) if prev_releases else 0,
            'history': []
        },
        'change_failure_rate': {
            'value': calculate_change_failure_rate(current_releases),
            'trend': calculate_change_failure_rate_trend(current_releases, prev_releases) if prev_releases else 0,
            'history': []
        },
        'time_to_restore': {
            'value': calculate_time_to_restore(current_incidents),
            'trend': calculate_time_to_restore_trend(current_incidents, prev_incidents) if prev_incidents else 0,
            'history': []
        }
    }

    return jsonify(metrics)

@bp.route('/deployment-volume', methods=['GET'])
@login_required
def get_deployment_volume():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Parse dates
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    if (start_date and not start) or (end_date and not end):
        return jsonify({'error': 'Invalid date format, expected ISO-8601'}), 400
    
    query = db.session.query(
        Release.platform,
        Release.rollout_date,
        db.func.count(Release.id).label('count')
    ).group_by(Release.platform, Release.rollout_date)
    
    if start:
        query = query.filter(Release.rollout_date >= start)
    if end:
        query = query.filter(Release.rollout_date <= end)
    
    query = query.order_by(Release.rollout_date)  # Add ordering
    results = query.all()
    
    # Transform into format needed by chart
    data = {}
    for platform, date, count in results:
        date_str = date.isoformat()
        if date_str not in data:
            data[date_str] = {'date': date_str}
        data[date_str][platform] = count
    
    return jsonify(list(data.values()))

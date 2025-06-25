from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import and_
from .models import Release, Incident

def calculate_deployment_frequency(releases: List[Release], start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
    """Calculate deployments per day"""
    if not releases or len(releases) < 2:
        return 0.0
    
    filtered_releases = [r for r in releases if 
                        (not start_date or datetime.combine(r.rollout_date, datetime.min.time()) >= start_date) and
                        (not end_date or datetime.combine(r.rollout_date, datetime.min.time()) <= end_date)]
    
    if len(filtered_releases) < 2:
        return 0.0
        
    first_date = filtered_releases[0].rollout_date
    last_date = filtered_releases[-1].rollout_date
    days_diff = (last_date - first_date).days or 1  # Avoid division by zero
    
    return len(filtered_releases) / days_diff

def calculate_lead_time(releases: List[Release]) -> float:
    """Calculate average time from commit to deploy (in hours)"""
    successful_releases = [r for r in releases if r.is_successful]
    if not successful_releases:
        return 0.0
    
    # In a real system, this would calculate time from commit to deploy
    # For now, we'll use a placeholder average of 24 hours
    return 24.0

def calculate_change_failure_rate(releases: List[Release]) -> float:
    """Calculate percentage of deployments that failed"""
    if not releases:
        return 0.0
    
    failed_releases = len([r for r in releases if not r.is_successful])
    return (failed_releases / len(releases)) * 100

def calculate_time_to_restore(incidents: List[Incident]) -> float:
    """Calculate average time to restore service after failure (in hours)"""
    if not incidents:
        return 0.0
    
    restoration_times = []
    for incident in incidents:
        if incident.start_time and incident.end_time:
            duration = incident.end_time - incident.start_time
            restoration_times.append(duration.total_seconds() / 3600)  # Convert to hours
    
    if not restoration_times:
        return 0.0
        
    return sum(restoration_times) / len(restoration_times)

def calculate_trend(current_value: float, previous_value: float) -> float:
    """Calculate percentage change between two values"""
    if previous_value == 0:
        return 0.0 if current_value == 0 else 100.0
    return ((current_value - previous_value) / previous_value) * 100

def get_previous_period_dates(start_date: datetime, end_date: datetime) -> tuple[datetime, datetime]:
    """Calculate the start and end dates for the previous period"""
    period_length = end_date - start_date
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - period_length
    return previous_start, previous_end

def calculate_deployment_frequency_trend(releases: List[Release], start_date: datetime, end_date: datetime) -> float:
    """Calculate trend for deployment frequency"""
    current_freq = calculate_deployment_frequency(releases, start_date, end_date)
    
    prev_start, prev_end = get_previous_period_dates(start_date, end_date)
    prev_releases = [r for r in releases if 
                    datetime.combine(r.rollout_date, datetime.min.time()) >= prev_start and
                    datetime.combine(r.rollout_date, datetime.min.time()) <= prev_end]
    prev_freq = calculate_deployment_frequency(prev_releases, prev_start, prev_end)
    
    return calculate_trend(current_freq, prev_freq)

def calculate_lead_time_trend(current_releases: List[Release], previous_releases: List[Release]) -> float:
    """Calculate trend for lead time"""
    current_lead_time = calculate_lead_time(current_releases)
    previous_lead_time = calculate_lead_time(previous_releases)
    return calculate_trend(current_lead_time, previous_lead_time)

def calculate_change_failure_rate_trend(current_releases: List[Release], previous_releases: List[Release]) -> float:
    """Calculate trend for change failure rate"""
    current_rate = calculate_change_failure_rate(current_releases)
    previous_rate = calculate_change_failure_rate(previous_releases)
    return calculate_trend(current_rate, previous_rate)

def calculate_time_to_restore_trend(current_incidents: List[Incident], previous_incidents: List[Incident]) -> float:
    """Calculate trend for time to restore"""
    current_time = calculate_time_to_restore(current_incidents)
    previous_time = calculate_time_to_restore(previous_incidents)
    return calculate_trend(current_time, previous_time)

def get_filtered_releases(platform: Optional[str] = None, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[Release]:
    """Get releases filtered by platform and date range"""
    query = Release.query
    
    if platform:
        query = query.filter_by(platform=platform)
    
    if start_date:
        # Get releases from the previous period as well for trend calculation
        start_dt = datetime.fromisoformat(start_date)
        prev_start = start_dt - timedelta(days=30)  # Get extra month of data
        query = query.filter(Release.rollout_date >= prev_start.date())
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(Release.rollout_date <= end_dt.date())
    
    return query.order_by(Release.rollout_date).all()

def get_filtered_incidents(release_ids: List[int],
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[Incident]:
    """Get incidents for the given releases"""
    return Incident.query.filter(Incident.release_id.in_(release_ids)).all()


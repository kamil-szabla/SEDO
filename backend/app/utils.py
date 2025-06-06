from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import and_
from .models import Release, Incident

def calculate_deployment_frequency(releases: List[Release], start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
    """Calculate deployments per day"""
    if not releases or len(releases) < 2:
        return 0.0
    
    filtered_releases = [r for r in releases if 
                        (not start_date or r.rollout_date >= start_date) and
                        (not end_date or r.rollout_date <= end_date)]
    
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

def get_filtered_releases(platform: Optional[str] = None, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[Release]:
    """Get releases filtered by platform and date range"""
    query = Release.query
    
    if platform:
        query = query.filter_by(platform=platform)
    
    if start_date:
        query = query.filter(Release.rollout_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Release.rollout_date <= datetime.fromisoformat(end_date))
    
    return query.order_by(Release.rollout_date).all()

def get_filtered_incidents(release_ids: List[int],
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[Incident]:
    """Get incidents filtered by releases and date range"""
    query = Incident.query.filter(Incident.release_id.in_(release_ids))
    
    if start_date:
        query = query.filter(Incident.start_time >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Incident.end_time <= datetime.fromisoformat(end_date))
    
    return query.all()

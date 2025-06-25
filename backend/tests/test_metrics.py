import pytest
from datetime import datetime, timedelta
from app.models import Release, Incident
from app import db

PLATFORM_NAME = "TestPlatform"

@pytest.fixture
def login_test_user(client, test_user):
    client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    return client

@pytest.fixture
def test_data(app):
    """Create test releases and incidents."""
    with app.app_context():
        base_date = datetime.utcnow()

        # Create releases over a week
        releases = []
        for i in range(7):
            release = Release(
                platform=PLATFORM_NAME,
                release_type='feature',
                version=f'1.0.{i}',
                is_successful=(i < 5),
                rollout_date=base_date - timedelta(days=i)
            )
            releases.append(release)
            db.session.add(release)
        db.session.commit()

        # Create incidents for failed releases
        incidents = []
        for release in releases[5:]:  # Last two releases failed
            incident = Incident(
                release_id=release.id,
                start_time=datetime.combine(release.rollout_date, datetime.min.time()) + timedelta(hours=1),
                end_time=datetime.combine(release.rollout_date, datetime.min.time()) + timedelta(hours=3),
                description=f"Incident for release {release.version}"
            )
            incidents.append(incident)
            db.session.add(incident)
        db.session.commit()

        return {'releases': releases, 'incidents': incidents}


class TestMetrics:

    def test_get_metrics_success(self, login_test_user, test_data):
        response = login_test_user.get(f'/api/metrics/?platform={PLATFORM_NAME}')
        assert response.status_code == 200
        metrics = response.get_json()

        assert 'deployment_frequency' in metrics
        assert 'lead_time' in metrics
        assert 'change_failure_rate' in metrics
        assert 'time_to_restore' in metrics

        assert metrics['deployment_frequency']['value'] == pytest.approx(1.166, 0.1)
        assert metrics['change_failure_rate']['value'] == pytest.approx(28.57, 0.01)
        assert metrics['time_to_restore']['value'] == pytest.approx(2.0, 0.1)

    def test_get_metrics_with_date_filter(self, login_test_user, test_data):
        base_date = datetime.utcnow()
        start_date = (base_date - timedelta(days=3)).isoformat()
        end_date = base_date.isoformat()

        response = login_test_user.get(
            f'/api/metrics/?platform={PLATFORM_NAME}&start_date={start_date}&end_date={end_date}'
        )
        assert response.status_code == 200
        metrics = response.get_json()
        assert metrics['deployment_frequency']['value'] > 0
        assert metrics['change_failure_rate']['value'] < 28.57

    def test_get_metrics_invalid_date(self, login_test_user):
        response = login_test_user.get(
            f'/api/metrics/?platform={PLATFORM_NAME}&start_date=invalid-date')
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Invalid date format, expected ISO-8601'

    def test_get_metrics_no_releases(self, login_test_user):
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        response = login_test_user.get(
            f'/api/metrics/?platform={PLATFORM_NAME}&start_date={future_date}')
        assert response.status_code == 200
        assert response.get_json()['note'] == 'No releases found for the given criteria'

    def test_get_metrics_unauthorized(self, client):
        response = client.get('/api/metrics/')
        assert response.status_code == 401

    def test_get_metrics_different_platforms(self, login_test_user, app):
        with app.app_context():
            base_date = datetime.utcnow()

            # Platform A: All successful
            for i in range(3):
                db.session.add(Release(
                    platform='Platform A',
                    release_type='feature',
                    is_successful=True,
                    version=f'1.0.{i}',
                    rollout_date=base_date - timedelta(days=i)
                ))

            # Platform B: All failed + incidents
            for i in range(3):
                release = Release(
                    platform='Platform B',
                    release_type='feature',
                    is_successful=False,
                    version=f'2.0.{i}',
                    rollout_date=base_date - timedelta(days=i)
                )
                db.session.add(release)
                db.session.flush()
                db.session.add(Incident(
                    release_id=release.id,
                    start_time=release.rollout_date + timedelta(minutes=15),
                    end_time=release.rollout_date + timedelta(hours=1),
                    description='Failure'
                ))

            db.session.commit()

            r1 = login_test_user.get('/api/metrics/?platform=Platform A')
            r2 = login_test_user.get('/api/metrics/?platform=Platform B')

            assert r1.status_code == 200
            assert r2.status_code == 200
            assert r1.get_json()['change_failure_rate']['value'] == 0
            assert r2.get_json()['change_failure_rate']['value'] == 100
            assert r1.get_json()['time_to_restore']['value'] == 0
            assert r2.get_json()['time_to_restore']['value'] > 0

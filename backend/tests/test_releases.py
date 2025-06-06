import pytest
from datetime import datetime, timedelta
from app.models import Release
from app import db

# @pytest.fixture
# def test_platform(app):
#     """Create a test platform."""
#     with app.app_context():
#         platform = "TestPlatform"
#         db.session.add(platform)
#         db.session.commit()
#         return platform

class TestReleases:
    def test_add_release_success(self, client, admin_headers):
        """Test successful release creation by admin."""
        response = client.post('/api/releases/', json={
            'platform': 'TestPlatform',
            'release_type': 'feature',
            'is_successful': True,
            'version': '1.0.0'
        }, headers=admin_headers)

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['message'] == 'Release added'

        # Verify the release was created with correct data
        with client.application.app_context():
            release = Release.query.filter_by(version='1.0.0').first()
            assert release is not None
            assert release.platform == 'TestPlatform'
            assert release.release_type == 'feature'
            assert release.is_successful is True

    def test_add_release_unauthorized(self, client, auth_headers):
        """Test release creation by user without write privileges."""
        response = client.post('/api/releases/', json={
            'platform': 'TestPlatform',
            'release_type': 'feature',
            'is_successful': True,
            'version': '1.0.0'
        }, headers=auth_headers)

        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data['error'] == 'Write privileges required'

    def test_get_releases(self, client, auth_headers):
        """Test getting all releases."""
        # Create some test releases
        with client.application.app_context():
            releases = [
                Release(
                    platform='TestPlatform',
                    release_type='feature',
                    version='1.0.0',
                    is_successful=True
                ),
                Release(
                    platform='TestPlatform',
                    release_type='hotfix',
                    version='1.0.1',
                    is_successful=False
                )
            ]
            for release in releases:
                db.session.add(release)
            db.session.commit()

        response = client.get('/api/releases/', headers=auth_headers)
        assert response.status_code == 200
        releases = response.get_json()
        assert isinstance(releases, list)
        assert len(releases) == 2
        assert all(r['platform'] == 'TestPlatform' for r in releases)

    def test_get_releases_with_filters(self, client, auth_headers):
        """Test getting releases with date filters."""
        with client.application.app_context():
            
            # Create releases with different dates
            today = datetime.utcnow()
            yesterday = today - timedelta(days=1)
            tomorrow = today + timedelta(days=1)
            
            releases = [
                Release(platform="TestPlatform", release_type='feature', 
                    is_successful=True, version='1.0.0', rollout_date=yesterday),
                Release(platform='TestPlatform', release_type='feature', 
                    is_successful=True, version='1.0.1', rollout_date=today),
                Release(platform='TestPlatform', release_type='feature', 
                    is_successful=True, version='1.0.2', rollout_date=tomorrow)
            ]
            for release in releases:
                db.session.add(release)
            db.session.commit()

        # Test date filtering
        response = client.get(
            f'/api/releases/?start_date={yesterday.isoformat()}&end_date={(today + timedelta(days=1)).isoformat()}',
            headers=auth_headers
        )
        assert response.status_code == 200
        releases = response.get_json()
        assert len(releases) == 2

    def test_update_release_success(self, client, admin_headers, test_release):
        """Test successful release update."""
        response = client.put(f'/api/releases/{test_release.id}', json={
            'version': '2.0.0',
            'is_successful': False
        }, headers=admin_headers)

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == 'Release updated successfully'

        # Verify the update
        with client.application.app_context():
            updated_release = db.session.get(Release, test_release.id)
            assert updated_release.version == '2.0.0'
            assert updated_release.is_successful == False

    def test_update_release_unauthorized(self, client, auth_headers, test_release):
        """Test release update by user without write privileges."""
        response = client.put(f'/api/releases/{test_release.id}', json={
            'version': '2.0.0'
        }, headers=auth_headers)

        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data['error'] == 'Write privileges required'

    def test_update_release_not_found(self, client, admin_headers):
        """Test updating non-existent release."""
        response = client.put('/api/releases/9999', json={
            'version': '2.0.0'
        }, headers=admin_headers)

        assert response.status_code == 404

    def test_delete_release_success(self, client, admin_headers, test_release):
        """Test successful release deletion."""
        response = client.delete(f'/api/releases/{test_release.id}', 
                            headers=admin_headers)

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == 'Release deleted successfully'

        # Verify deletion
        with client.application.app_context():
            assert db.session.get(Release, test_release.id) is None

    def test_delete_release_unauthorized(self, client, auth_headers, test_release):
        """Test release deletion by user without write privileges."""
        response = client.delete(f'/api/releases/{test_release.id}', 
                            headers=auth_headers)

        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data['error'] == 'Write privileges required'

    def test_delete_release_not_found(self, client, admin_headers):
        """Test deleting non-existent release."""
        response = client.delete('/api/releases/9999', headers=admin_headers)
        assert response.status_code == 404

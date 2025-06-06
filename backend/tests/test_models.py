import pytest
from datetime import datetime
from app.models import User, Release, Incident
from app import db

class TestModels:
    def test_user_creation(self, app):
        """Test User model creation and attributes."""
        with app.app_context():
            user = User(
                username='testuser',
                password_hash='hashedpassword',
                role='user'
            )
            db.session.add(user)
            db.session.commit()

            retrieved_user = User.query.filter_by(username='testuser').first()
            assert retrieved_user is not None
            assert retrieved_user.username == 'testuser'
            assert retrieved_user.password_hash == 'hashedpassword'
            assert retrieved_user.role == 'user'

    def test_user_to_dict(self, app):
        """Test User model to_dict method."""
        with app.app_context():
            user = User(
                username='testuser',
                password_hash='hashedpassword',
                role='user'
            )
            db.session.add(user)
            db.session.commit()

            user_dict = user.to_dict()
            assert isinstance(user_dict, dict)
            assert user_dict['username'] == 'testuser'
            assert user_dict['role'] == 'user'
            assert 'password_hash' not in user_dict  # Ensure sensitive data is not included

    def test_release_creation(self, app):
        """Test Release model creation and relationships."""
        with app.app_context():
            release = Release(
                platform="TestPlatform",
                release_type='feature',
                is_successful=True,
                version='1.0.0',
                rollout_date=datetime.utcnow()
            )
            db.session.add(release)
            db.session.commit()

            retrieved_release = Release.query.filter_by(version='1.0.0').first()
            assert retrieved_release is not None
            assert retrieved_release.platform == "TestPlatform"
            assert retrieved_release.release_type == 'feature'
            assert retrieved_release.is_successful is True
            assert isinstance(retrieved_release.rollout_date, datetime)

    def test_release_to_dict(self, app):
        """Test Release model to_dict method."""
        with app.app_context():

            release_date = datetime.utcnow()
            release = Release(
                platform="TestPlatform",
                release_type='feature',
                is_successful=True,
                version='1.0.0',
                rollout_date=release_date
            )
            db.session.add(release)
            db.session.commit()

            release_dict = release.to_dict()
            assert isinstance(release_dict, dict)
            assert release_dict['platform'] == "TestPlatform"
            assert release_dict['version'] == '1.0.0'
            assert release_dict['release_type'] == 'feature'
            assert release_dict['is_successful'] is True
            assert release_dict['rollout_date'] == release_date.isoformat()

    def test_incident_creation(self, app):
        """Test Incident model creation and relationships."""
        with app.app_context():

            release = Release(
                platform='TestPlatform',
                release_type='feature',
                version='1.0.0'
            )
            db.session.add(release)
            db.session.commit()

            start_time = datetime.utcnow()
            end_time = datetime.utcnow()
            incident = Incident(
                release_id=release.id,
                start_time=start_time,
                end_time=end_time,
                description='Test incident'
            )
            db.session.add(incident)
            db.session.commit()

            retrieved_incident = Incident.query.filter_by(release_id=release.id).first()
            assert retrieved_incident is not None
            assert retrieved_incident.release_id == release.id
            assert retrieved_incident.description == 'Test incident'
            assert retrieved_incident.start_time == start_time
            assert retrieved_incident.end_time == end_time

    def test_cascade_delete(self, app):
        """Test cascade delete behavior between models."""
        with app.app_context():

            # Create a release for the platform
            release = Release(
                platform='TestPlatform',
                release_type='feature',
                version='1.0.0'
            )
            db.session.add(release)
            db.session.commit()

            # Create an incident for the release
            incident = Incident(
                release_id=release.id,
                description='Test incident'
            )
            db.session.add(incident)
            db.session.commit()

            incident_id = incident.id

            db.session.delete(release)
            db.session.commit()

            # Verify that release and incident are deleted
            assert Release.query.filter_by(id=release.id).first() is None
            assert Incident.query.filter_by(id=incident_id).first() is None

    def test_model_constraints(self, app):
        """Test model constraints and required fields."""
        with app.app_context():
            # Test User model constraints
            user = User(password_hash='hashedpassword', role='user')  # Missing username
            db.session.add(user)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

            # Test Release model constraints
            release = Release(version='1.0.0')  # Missing platform
            db.session.add(release)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

            # Test Incident model constraints
            incident = Incident(description='Test incident')  # Missing release_id
            db.session.add(incident)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

import os
import tempfile
import pytest
from sqlalchemy import text
from app import create_app, db, bcrypt
from app.models import User, Release
from datetime import datetime

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    }
    app = create_app(config)

    with app.app_context():
        db.create_all()
        db.session.execute(text('PRAGMA foreign_keys=ON'))
        yield app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            username='testuser',
            password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        return user.id

@pytest.fixture
def test_admin(app):
    with app.app_context():
        admin = User(
            username='admin',
            password_hash=bcrypt.generate_password_hash('admin').decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        return admin.id

@pytest.fixture
def test_release(app):
    with app.app_context():

        release = Release(
            platform='testPlatform',
            release_type='feature',
            version='1.0.0',
            is_successful=True,
            rollout_date=datetime.utcnow()
        )
        db.session.add(release)
        db.session.commit()
        db.session.refresh(release)
        return release

@pytest.fixture
def auth_headers(client, test_user):
    client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    return {'Content-Type': 'application/json'}

@pytest.fixture
def admin_headers(client, test_admin):
    client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin'
    })
    return {'Content-Type': 'application/json'}

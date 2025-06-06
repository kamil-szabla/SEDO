import pytest
from flask import session
from app.models import User

class TestAuth:

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'message' in json_data
        assert json_data['message'] == 'Logged in successfully'
        assert 'user' in json_data
        assert json_data['user']['username'] == 'testuser'
        assert json_data['user']['role'] == 'user'

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'Invalid credentials'

    def test_login_missing_username(self, client):
        """Test login with missing username."""
        response = client.post('/api/auth/login', json={
            'password': 'password123'
        })
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'Username and password required'

    def test_login_missing_password(self, client):
        """Test login with missing password."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
        })
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'Username and password required'

    def test_login_no_json(self, client):
        """Test login with no JSON data."""
        response = client.post('/api/auth/login')
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'No data provided'

    def test_login_nonexistent_user(self, client):
        """Test login with a username that doesn't exist."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistentuser',
            'password': 'password123'
        })
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'Invalid credentials'

    def test_logout_success(self, client, test_user):
        """Test successful logout."""
        # Log in first — this sets session cookies in the test client
        login_response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        assert login_response.status_code == 200

        # Reuse the same client for logout
        logout_response = client.post('/api/auth/logout')
        assert logout_response.status_code == 200
        json_data = logout_response.get_json()
        assert json_data['message'] == 'Logged out successfully'


    def test_logout_without_login(self, client):
        """Test logout without being logged in."""
        response = client.post('/api/auth/logout')
        assert response.status_code == 401  # Unauthorized

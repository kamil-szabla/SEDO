import pytest
from app.models import User
from app import db, bcrypt

def set_password_hash(password):
    """Helper function to create password hash."""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def test_get_users_admin(client, test_admin, admin_headers):
    """Test getting all users as admin."""
    response = client.get('/api/users/', headers=admin_headers)
    assert response.status_code == 200
    users = response.get_json()
    assert isinstance(users, list)
    assert len(users) > 0
    assert all(key in users[0] for key in ['id', 'username', 'role'])

def test_get_users_unauthorized(client, test_user, auth_headers):
    """Test getting users as non-admin user."""
    response = client.get('/api/users/', headers=auth_headers)
    assert response.status_code == 403
    error = response.get_json()
    assert error['error'] == 'Admin privileges required'

def test_create_user_success(client, test_admin, admin_headers):
    """Test successful user creation by admin."""
    response = client.post('/api/users/', json={
        'username': 'newuser',
        'password': 'password123',
        'role': 'writer'
    }, headers=admin_headers)

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == 'User created successfully'

    # Verify user was created
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.role == 'writer'
        assert bcrypt.check_password_hash(user.password_hash, 'password123')

def test_create_user_duplicate_username(client, test_admin, admin_headers, test_user):
    """Test creating user with existing username."""
    response = client.post('/api/users/', json={
        'username': 'testuser',  # Same as test_user
        'password': 'password123'
    }, headers=admin_headers)

    assert response.status_code == 400
    error = response.get_json()
    assert error['error'] == 'Username already exists'

def test_create_user_missing_data(client, test_admin, admin_headers):
    """Test creating user with missing required fields."""
    response = client.post('/api/users/', json={
        'username': 'newuser'
        # Missing password
    }, headers=admin_headers)

    assert response.status_code == 400
    error = response.get_json()
    assert error['error'] == 'Username and password are required'

def test_update_user_success(client, test_admin, admin_headers, test_user):
    """Test successful user update by admin."""
    response = client.put(f'/api/users/{test_user}', json={
        'username': 'updateduser',
        'password': 'newpassword123',
        'role': 'writer'
    }, headers=admin_headers)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'User updated successfully'

    # Verify update
    with client.application.app_context():
        updated_user = db.session.get(User, test_user)
        assert updated_user.username == 'updateduser'
        assert updated_user.role == 'writer'
        assert bcrypt.check_password_hash(updated_user.password_hash, 'newpassword123')

def test_update_user_duplicate_username(client, test_admin, admin_headers, test_user):
    """Test updating user with existing username."""
    # Create another user first
    with client.application.app_context():
        other_user = User(
            username='otheruser',
            password_hash=set_password_hash('password123'),
            role='user'
        )
        db.session.add(other_user)
        db.session.commit()
        other_id = other_user.id

    response = client.put(f'/api/users/{other_id}', json={
        'username': 'testuser'  # Same as test_user
    }, headers=admin_headers)

    assert response.status_code == 400
    error = response.get_json()
    assert error['error'] == 'Username already exists'

def test_update_user_not_found(client, test_admin, admin_headers):
    """Test updating non-existent user."""
    response = client.put('/api/users/9999', json={
        'username': 'newname'
    }, headers=admin_headers)

    assert response.status_code == 404

def test_update_user_unauthorized(client, test_user, auth_headers):
    """Test user update by non-admin user."""
    response = client.put(f'/api/users/{test_user}', json={
        'username': 'newname'
    }, headers=auth_headers)

    assert response.status_code == 403
    error = response.get_json()
    assert error['error'] == 'Admin privileges required'

def test_delete_user_success(client, test_admin, admin_headers, test_user):
    """Test successful user deletion by admin."""
    response = client.delete(f'/api/users/{test_user}', 
                           headers=admin_headers)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'User deleted successfully'

    # Verify deletion
    with client.application.app_context():
        assert db.session.get(User, test_user) is None

def test_delete_self(client, test_admin, admin_headers):
    """Test admin attempting to delete their own account."""
    response = client.delete(f'/api/users/{test_admin}', 
                           headers=admin_headers)

    assert response.status_code == 400
    error = response.get_json()
    assert error['error'] == 'Cannot delete your own account'

def test_delete_user_not_found(client, test_admin, admin_headers):
    """Test deleting non-existent user."""
    response = client.delete('/api/users/9999', headers=admin_headers)
    assert response.status_code == 404

def test_delete_user_unauthorized(client, test_user, auth_headers):
    """Test user deletion by non-admin user."""
    response = client.delete(f'/api/users/{test_user}', 
                           headers=auth_headers)

    assert response.status_code == 403
    error = response.get_json()
    assert error['error'] == 'Admin privileges required'

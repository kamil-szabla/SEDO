from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db, bcrypt

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True)
        if not data:
            current_app.logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        if 'username' not in data or 'password' not in data:
            current_app.logger.error("Missing username or password")
            return jsonify({'error': 'Username and password required'}), 400
            
        user = User.query.filter_by(username=data['username']).first()
        current_app.logger.info(f"Login attempt for user: {data['username']}")
        
        if user and bcrypt.check_password_hash(user.password_hash, data['password']):
            login_user(user)
            current_app.logger.info(f"User {user.username} logged in successfully")
            return jsonify({
                'message': 'Logged in successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            }), 200
            
        current_app.logger.warning(f"Failed login attempt for user: {data['username']}")
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

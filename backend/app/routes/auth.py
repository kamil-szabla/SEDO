from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db, bcrypt

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(silent=True)
        if not data:
            current_app.logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        if 'username' not in data or 'password' not in data:
            current_app.logger.error("Missing username or password")
            return jsonify({'error': 'Username and password required'}), 400
            
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            current_app.logger.warning(f"Registration failed: Username {data['username']} already exists")
            return jsonify({'error': 'Username already exists'}), 400

        # Check if email is already registered
        if 'email' in data and data['email']:
            if User.query.filter_by(email=data['email']).first():
                current_app.logger.warning(f"Registration failed: Email {data['email']} already exists")
                return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(
            username=data['username'],
            email=data.get('email'),  # Email is optional in the database
            password_hash=password_hash,
            role=data.get('role', 'user')  # Default role is 'user'
        )
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f"User {user.username} registered successfully")
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 201
            
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/status', methods=['GET'])
def status():
    return jsonify({'authenticated': current_user.is_authenticated})

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

from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from app.models import User
from app import db, bcrypt
from functools import wraps

bp = Blueprint('users', __name__, url_prefix='/api/users')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/', methods=['GET'])
@login_required
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'role': user.role
    } for user in users])

@bp.route('/', methods=['POST'])
@login_required
@admin_required
def create_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        username=data['username'],
        password_hash=password_hash,
        role=data.get('role', 'user')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201


@bp.route('/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    data = request.get_json()
    
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']
    
    if 'password' in data:
        user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

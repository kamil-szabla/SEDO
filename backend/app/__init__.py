from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
from config import Config
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    CORS(app, supports_credentials=True)
    
    login_manager.login_view = None
    login_manager.unauthorized_handler(lambda: (jsonify({'error': 'Unathorized'}), 401))
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        from . import db
        return db.session.get(User, int(user_id))

    from .routes import auth, releases, metrics, users
    app.register_blueprint(auth.bp)
    app.register_blueprint(releases.bp)
    app.register_blueprint(metrics.bp)
    app.register_blueprint(users.bp)

    return app

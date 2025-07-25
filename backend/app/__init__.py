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


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config.update({
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "None",
        "SESSION_COOKIE_SECURE": True, 
        "SESSION_COOKIE_PATH": "/",
        # "SESSION_COOKIE_DOMAIN": ".onrender.com",
        })

    if config_overrides:
        app.config.update(config_overrides)

    CORS(app, 
        origins=["http://localhost:5173", "https://dora-ui.onrender.com"], 
        supports_credentials=True,
        expose_headers=["Set-Cookie"],
        allow_headers=["Content-Type", "Authorization"])

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
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

    @app.after_request
    def apply_security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    return app

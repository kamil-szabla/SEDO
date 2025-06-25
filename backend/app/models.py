from . import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Date

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

class Release(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String, nullable=False)
    release_type = db.Column(db.String(50))
    is_successful = db.Column(db.Boolean, default=True)
    version = db.Column(db.String(20))
    rollout_date = db.Column(Date, default=lambda: datetime.utcnow().date())
    mcm_link = db.Column(db.String(512))
    ci_job_link = db.Column(db.String(512))
    commit_list_link = db.Column(db.String(512))
    incident = db.relationship('Incident', backref='release', cascade='all, delete-orphan', passive_deletes=True)

    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'version': self.version,
            'release_type': self.release_type,
            'is_successful': self.is_successful,
            'rollout_date': self.rollout_date.isoformat(),
            'mcm_link': self.mcm_link,
            'ci_job_link': self.ci_job_link,
            'commit_list_link': self.commit_list_link
        }

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    release_id = db.Column(db.Integer, db.ForeignKey('release.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    description = db.Column(db.Text)

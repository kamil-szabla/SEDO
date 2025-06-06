from app import create_app, db
from app.models import User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            password_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
            admin = User(username='admin', password_hash=password_hash, role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")
        
        print("Database initialized successfully")

if __name__ == '__main__':
    init_db()

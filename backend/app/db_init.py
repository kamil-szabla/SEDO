from app import create_app, db
from app.models import User, Release
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import random
import os

def random_date(start, end):
    """Return random datetime between `start` and `end`."""
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def generate_dummy_releases(n=200):
    platforms = ['Android', 'Samsung', 'Roku', 'Xbox', 'PS4', 'PS5']
    release_types = ['release', 'rollback']

    releases = []
    for i in range(n):
        rollout_date = random_date(datetime.now() - timedelta(days=90), datetime.now())
        version = f"{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}"

        release = Release(
            platform=random.choice(platforms),
            release_type=random.choice(release_types),
            is_successful=random.choice([True, False]),
            version=version,
            rollout_date=rollout_date,
            mcm_link=f"https://mcm.example.com/release/{version}",
            ci_job_link=f"https://ci.example.com/job/{version}",
            commit_list_link=f"https://git.example.com/commits/{version}"
        )
        releases.append(release)

    return releases

def init_db():
    app = create_app()
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created")
        
        # Check if we should initialize data
        if os.getenv('INITIALIZE_DATA') == 'true':
            # Create admin user if doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                password_hash = bcrypt.generate_password_hash('admin').decode('utf-8')
                admin = User(
                    username='admin',
                    password_hash=password_hash,
                    role='admin',
                    email='admin@example.com'
                )
                db.session.add(admin)
                print("Admin user created")
            
            # Create test user if doesn't exist
            test_user = User.query.filter_by(username='test').first()
            if not test_user:
                password_hash = bcrypt.generate_password_hash('test123').decode('utf-8')
                test_user = User(
                    username='test',
                    password_hash=password_hash,
                    role='user',
                    email='test@example.com'
                )
                db.session.add(test_user)
                print("Test user created")

            # Create dummy releases if none exist
            if Release.query.count() == 0:
                dummy_releases = generate_dummy_releases(200)
                db.session.add_all(dummy_releases)
                print("Dummy releases created")
            
            db.session.commit()
            print("Database initialized with default data")
        else:
            print("Skipping data initialization (INITIALIZE_DATA != true)")

if __name__ == '__main__':
    init_db()

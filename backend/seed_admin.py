from app import app
from db import db
from models import User
from werkzeug.security import generate_password_hash

def seed_admin():
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@uni.edu').first()
        if not admin:
            admin = User(
                email='admin@uni.edu',
                password_hash=generate_password_hash('admin@123'),
                role='admin',
                status='Active'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin@uni.edu / admin@123")
        else:
            admin.status = 'Active' # Ensure active
            db.session.commit()
            print("Admin user already exists.")

if __name__ == '__main__':
    seed_admin()

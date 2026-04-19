from app import app
from db import db
from models import User
from sqlalchemy import text

def update_emails():
    with app.app_context():
        print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("Searching for emails ending in @edu.com...")
        users = User.query.filter(User.email.like('%@edu.com')).all()
        
        if not users:
            print("No @edu.com emails found to update.")
            return

        print(f"Updating {len(users)} users...")
        for user in users:
            old_email = user.email
            new_email = old_email.replace('@edu.com', '@uni.edu')
            user.email = new_email
            print(f"  - {old_email} -> {new_email}")

        try:
            db.session.commit()
            print("Successfully updated all emails to @uni.edu!")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating emails: {e}")

if __name__ == '__main__':
    update_emails()

from app import app
from db import db
from models import User
from werkzeug.security import generate_password_hash

def update_passwords():
    new_password = "Research@Hub2024!"
    with app.app_context():
        print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Updating all user passwords to: {new_password}")
        
        users = User.query.all()
        new_hash = generate_password_hash(new_password)
        
        for user in users:
            user.password_hash = new_hash
            print(f"  - Updated: {user.email}")
            
        try:
            db.session.commit()
            print("Successfully updated all passwords in the database!")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating passwords: {e}")

if __name__ == '__main__':
    update_passwords()

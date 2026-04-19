from app import app
from db import db
from models import User
from werkzeug.security import generate_password_hash

def update_dynamic_passwords():
    with app.app_context():
        print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        users = User.query.all()
        
        print("Updating passwords to [email_prefix]@123 pattern (min 8 chars)...")
        for user in users:
            if not user.email: continue
            prefix = user.email.split('@')[0]
            password = f"{prefix}@123"
            
            # Ensure 8 character minimum by padding if necessary
            if len(password) < 8:
                password = password.ljust(8, '0')
                
            user.password_hash = generate_password_hash(password)
            print(f"  - {user.email} -> {password}")
            
        try:
            db.session.commit()
            print("Successfully updated all database passwords!")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating passwords: {e}")

if __name__ == '__main__':
    update_dynamic_passwords()

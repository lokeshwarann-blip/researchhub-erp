from flask import Flask
from flask_cors import CORS
from db import db
from routes.auth import auth_bp
from routes.scholar import scholar_bp
from routes.supervisor import supervisor_bp
from routes.milestones import milestones_bp
from routes.documents import documents_bp
from routes.publications import publications_bp
from routes.stipend import stipend_bp
from routes.leave import leave_bp
from routes.messages import messages_bp
from routes.meetings import meetings_bp
from routes.admin import admin_bp
from routes.attendance import attendance_bp
from routes.notifications import notifications_bp
import os
from werkzeug.security import generate_password_hash
from models import User

app = Flask(__name__)
CORS(app)

# ── Database Config ───────────────────────────────────────────────────────────
if os.environ.get('RENDER'):
    # On Render, use SQLite for simplicity (free tier)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///researchhub.db'
else:
    # On Local, use MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/researchhub'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# ── Register Blueprints ───────────────────────────────────────────────────────
app.register_blueprint(auth_bp,         url_prefix='/api/auth')
app.register_blueprint(scholar_bp,      url_prefix='/api/scholar')
app.register_blueprint(supervisor_bp,   url_prefix='/api/supervisor')
app.register_blueprint(milestones_bp,   url_prefix='/api/milestones')
app.register_blueprint(documents_bp,    url_prefix='/api/documents')
app.register_blueprint(publications_bp, url_prefix='/api/publications')
app.register_blueprint(stipend_bp,      url_prefix='/api/stipend')
app.register_blueprint(leave_bp,        url_prefix='/api/leave')
app.register_blueprint(messages_bp,     url_prefix='/api/messages')
app.register_blueprint(meetings_bp,     url_prefix='/api/meetings')
app.register_blueprint(admin_bp,        url_prefix='/api/admin')
app.register_blueprint(attendance_bp,   url_prefix='/api/attendance')
app.register_blueprint(notifications_bp,url_prefix='/api/notifications')

# ── Create all tables on first run ───────────────────────────────────────────
with app.app_context():
    from models import Scholar, Supervisor
    db.create_all()
    
    # Check if database is empty
    if not User.query.filter_by(role='admin').first():
        # 1. ADMIN
        admin = User(email='admin@uni.edu', password_hash=generate_password_hash('Admin@123'), role='admin', status='Active')
        db.session.add(admin)
        
        # 2. SUPERVISORS
        supervisors = []
        su_data = [
            ('Sarah', 'Johnson', 'sarah@uni.edu', 'Professor', 'CS'),
            ('James', 'Miller', 'james@uni.edu', 'Asst. Professor', 'IT')
        ]
        for f, l, e, d, dept in su_data:
            u = User(email=e, password_hash=generate_password_hash('Admin@123'), role='supervisor', status='Active')
            db.session.add(u)
            db.session.flush()
            s = Supervisor(user_id=u.id, first_name=f, last_name=l, department=dept, designation=d, university='Anna University')
            db.session.add(s)
            db.session.flush()
            supervisors.append(s)

        # 3. SCHOLARS
        sc_data = [
            ('Elena', 'Vance', 'elena@uni.edu', 'RH2024001', 'CS', supervisors[0].id),
            ('Marcus', 'Fenix', 'marcus@uni.edu', 'RH2024002', 'IT', supervisors[1].id)
        ]
        for f, l, e, en, dept, sid in sc_data:
            u = User(email=e, password_hash=generate_password_hash('Admin@123'), role='scholar', status='Active')
            db.session.add(u)
            db.session.flush()
            s = Scholar(user_id=u.id, first_name=f, last_name=l, enrollment_id=en, department=dept, enroll_year=2024, university='Anna University', supervisor_id=sid)
            db.session.add(s)

        db.session.commit()
        print("SUCCESS: Full production dataset seeded.")

    print("SUCCESS: Database initialized successfully.")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

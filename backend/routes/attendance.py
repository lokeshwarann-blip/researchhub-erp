from flask import Blueprint, request, jsonify
from db import db
from models import Attendance, Scholar
from datetime import date

attendance_bp = Blueprint('attendance', __name__)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/attendance/<scholar_id>?month=4&year=2025
# ─────────────────────────────────────────────────────────────────────────────
@attendance_bp.route('/<int:scholar_id>', methods=['GET'])
def get_attendance(scholar_id):
    month = request.args.get('month', type=int)
    year  = request.args.get('year', type=int)
    q = Attendance.query.filter_by(scholar_id=scholar_id)
    if month and year:
        from sqlalchemy import extract
        q = q.filter(extract('month', Attendance.date) == month,
                     extract('year',  Attendance.date) == year)
    records = q.order_by(Attendance.date).all()
    # Month Summary
    total   = len(records)
    present = sum(1 for r in records if r.status == 'present')
    absent  = sum(1 for r in records if r.status == 'absent')
    on_leave= sum(1 for r in records if r.status == 'leave')

    # Overall Summary for Pie Chart
    all_recs = Attendance.query.filter_by(scholar_id=scholar_id).all()
    overall = {
        'present': sum(1 for r in all_recs if r.status == 'present'),
        'absent': sum(1 for r in all_recs if r.status == 'absent'),
        'leave': sum(1 for r in all_recs if r.status == 'leave')
    }

    # Monthly Trend (Last 6 months)
    from sqlalchemy import extract
    import calendar
    monthly_trend = []
    today = date.today()
    for i in range(5, -1, -1):
        m = (today.month - i - 1) % 12 + 1
        y = today.year + (today.month - i - 1) // 12
        m_name = calendar.month_name[m][:3]
        m_recs = Attendance.query.filter_by(scholar_id=scholar_id).filter(extract('month', Attendance.date) == m, extract('year', Attendance.date) == y).all()
        monthly_trend.append({
            'label': m_name,
            'present': sum(1 for r in m_recs if r.status == 'present'),
            'absent': sum(1 for r in m_recs if r.status == 'absent')
        })

    return jsonify({
        'records' : [r.to_dict() for r in records],
        'summary' : {'total': total, 'present': present, 'absent': absent, 'leave': on_leave},
        'overall' : overall,
        'monthly' : monthly_trend,
        'pct'     : round(present / total * 100) if total else 0,
    }), 200


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/attendance/  — mark attendance (faculty action)
# Body: {scholar_id, date, status, marked_by}
# ─────────────────────────────────────────────────────────────────────────────
@attendance_bp.route('/', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    scholar_id = data.get('scholar_id')
    dt         = data.get('date')       # "YYYY-MM-DD"
    status     = data.get('status', 'present')
    marked_by  = data.get('marked_by')

    parsed_date = date.fromisoformat(dt) if dt else date.today()

    # Upsert: update if exists, else create
    existing = Attendance.query.filter_by(scholar_id=scholar_id, date=parsed_date).first()
    if existing:
        existing.status    = status
        existing.marked_by = marked_by
    else:
        db.session.add(Attendance(scholar_id=scholar_id, date=parsed_date,
                                  status=status, marked_by=marked_by))
    db.session.commit()
    return jsonify({'message': 'Attendance marked'}), 200

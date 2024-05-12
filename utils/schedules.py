from datetime import datetime, timedelta
from celery import Celery
from models import InstAttendance, db, app

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)


cel_app = Celery('schedules', backend='redis://localhost:6379', broker='redis://localhost:6379')


# @cel_app.task
# def checker(start_time):
#     now = datetime.now()
#     diff = start_time - now
#     if round(diff.total_seconds() / 60) >= 15:
#         return True
#     return False

@cel_app.task
def delete_records(start_time, id):
    now = datetime.now()
    diff = start_time - now
    try:
        with app.app_context():
            session = InstAttendance.query.filter_by(id=id).first()
        if not session:
            raise ValueError("")
    except Exception as e:
        return e

    if not session.verified and round(diff.total_seconds() / 60) >= 15:
        with app.app_context():
            db.session.delete(session)
            db.session.commit()
            print('deleted')
            return True
    print('not deleted')
    return False
    # print('delayed_task')



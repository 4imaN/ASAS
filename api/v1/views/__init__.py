

from flask import Blueprint

app_views = Blueprint('app', __name__, url_prefix='/api/v1')
from api.v1.views.admin_routes import *
from api.v1.views.instructor_routes import *
from api.v1.views.student_route import *
from api.v1.auth.jwt_auth import *
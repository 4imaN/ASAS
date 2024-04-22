#!/usr/bin/env python3
from models import db, app
from flask_admin import Admin


app.config['SECRET_KEY'] = "secret"


if __name__ == '__main__':
    app.run(debug=True)
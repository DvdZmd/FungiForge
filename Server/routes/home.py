from flask import Blueprint, render_template, redirect, url_for, session, request
from functools import wraps
#from requests import request
from config import AVAILABLE_RESOLUTIONS, READ_I2C_SENSORS, READ_SERVOS, INVERT_PAN_AXIS, INVERT_TILT_AXIS

home_bp = Blueprint('home', __name__)

@home_bp.before_request
def require_login():
    if 'user_id' not in session and request.endpoint != 'auth.login':
        return redirect(url_for('auth.login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@home_bp.route('/')
@login_required
def index():
    return render_template('index.html', 
                           resolutions=AVAILABLE_RESOLUTIONS, 
                           read_i2c_sensors=READ_I2C_SENSORS, 
                           read_servos=READ_SERVOS,
                           inverted_pan = INVERT_PAN_AXIS,
                           inverted_tilt = INVERT_TILT_AXIS)

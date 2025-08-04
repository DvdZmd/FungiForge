from flask import Blueprint, render_template, request, redirect, url_for, session
from auth.oauth2_server import authorization
from database.models import db, User


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # ✅ Here you could generate a token and redirect
        session['user_id'] = user.id
        return redirect(url_for('home.index'))  # or wherever your landing page is
        #return "Login successful!"  # Later: redirect or set session
    else:
        return "Invalid credentials", 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form['username']
    password = request.form['password']
    if User.query.filter_by(username=username).first():
        return "Username already exists", 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'buyer')
        full_name = request.form.get('full_name', '')

        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return render_template('auth/register.html')

        password_hash = generate_password_hash(password)
        db = get_db()

        try:
            db.execute(
                '''INSERT INTO users (username, email, password_hash, role, full_name)
                   VALUES (?, ?, ?, ?, ?)''',
                (username, email, password_hash, role, full_name)
            )
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

        except Exception:
            flash('Username or email already exists!', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        db = get_db()
        user_row = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user_row and check_password_hash(user_row['password_hash'], password):
            user = User(user_row['id'], user_row['username'], user_row['role'], user_row['full_name'])
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('buyer.dashboard') if user.is_buyer() else url_for('seller.dashboard'))

        flash('Invalid email or password!', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

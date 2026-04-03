from flask import Blueprint, render_template
from flask_login import login_required, current_user
from database import get_db

buyer_bp = Blueprint('buyer', __name__, template_folder='templates/buyer')


@buyer_bp.route('/buyer/dashboard')
@login_required
def dashboard():
    db = get_db()
    orders = db.execute('SELECT * FROM orders WHERE buyer_id = ?', (current_user.id,)).fetchall()
    return render_template('buyer/dashboard.html', orders=orders)

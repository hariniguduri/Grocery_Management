from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required

payment_bp = Blueprint('payment', __name__, template_folder='templates/checkout')


@payment_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        flash('Payment processed successfully!', 'success')
        return redirect(url_for('buyer.dashboard'))
    return render_template('checkout/payment.html')

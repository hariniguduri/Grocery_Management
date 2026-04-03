from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required
from database import get_db

checkout_bp = Blueprint('checkout', __name__, template_folder='templates/checkout')


@checkout_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # In production this would create an order and more.
        flash('Checkout complete. Proceed to payment.', 'success')
        return redirect(url_for('payment.payment'))

    cart_items = session.get('cart', {})
    db = get_db()
    products = []
    total = 0.0
    for product_id, quantity in cart_items.items():
        product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if product:
            subtotal = product['price'] * quantity
            total += subtotal
            products.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return render_template('checkout/checkout.html', items=products, total=total)

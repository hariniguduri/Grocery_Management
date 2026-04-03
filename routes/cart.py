from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db

cart_bp = Blueprint('cart', __name__, template_folder='templates/cart')


def _cart_key():
    return 'cart'  # simplified per-session cart


@cart_bp.route('/cart')
def cart_view():
    cart_items = session.get(_cart_key(), {})
    db = get_db()
    products = []
    total = 0.0
    for product_id, quantity in cart_items.items():
        product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if product:
            subtotal = product['price'] * quantity
            total += subtotal
            products.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return render_template('cart/cart.html', items=products, total=total)


@cart_bp.route('/cart/add', methods=['POST'])
@cart_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id=None):
    if product_id is None:
        product_id = int(request.form.get('product_id', 0))
    cart_items = session.get(_cart_key(), {})
    cart_items[str(product_id)] = cart_items.get(str(product_id), 0) + 1
    session[_cart_key()] = cart_items
    flash('Product added to cart.', 'success')
    return redirect(url_for('catalog.detail', product_id=product_id))


@cart_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart_items = session.get(_cart_key(), {})
    if str(product_id) in cart_items:
        cart_items.pop(str(product_id), None)
        session[_cart_key()] = cart_items
    flash('Product removed from cart.', 'info')
    return redirect(url_for('cart.cart_view'))

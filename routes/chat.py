from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import re

from database import get_db

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/', methods=['GET'])
@login_required
def chatbot():
    return render_template('chatbot.html')


def _extract_search_terms(message: str) -> str:
    stopwords = {
        'how', 'much', 'is', 'the', 'a', 'an', 'please', 'what', 'does', 'do',
        'of', 'cost', 'price', 'per', 'for', 'in', 'my', 'me', 'on', 'and', 'or',
        'to', 'show', 'tell', 'about', 'find', 'it', 'that', 'with', 'your',
        'can', 'i', 'you', 'help', 'ask', 'same', 'ans', 'why', 'is', 'price',
        'cost', 'prise'
    }
    tokens = re.findall(r"[a-zA-Z0-9]+", message.lower())
    terms = [token for token in tokens if token not in stopwords]
    return ' '.join(terms)


def _search_products(message: str):
    search_text = _extract_search_terms(message)
    if not search_text:
        return []

    query = '%' + '%'.join(search_text.split()) + '%'
    db = get_db()
    return db.execute(
        "SELECT name, price, unit FROM products WHERE lower(name) LIKE ? OR lower(description) LIKE ? LIMIT 5",
        (query, query),
    ).fetchall()


def generate_chat_response(message: str) -> str:
    message_lower = message.lower().strip()

    if not message_lower:
        return 'Please type a question about products, your cart, checkout, or account.'

    if any(keyword in message_lower for keyword in ['price', 'cost', 'how much', 'rate']):
        products = _search_products(message_lower)
        if products:
            product = products[0]
            return f"The price of {product['name']} is ₹{product['price']} per {product['unit']}."
        return 'I could not find that product in the catalog. Try a different name or category.'

    if 'order' in message_lower:
        return 'You can review your cart and checkout page for order details. Ask me about products, delivery, or payment options.'

    if 'cart' in message_lower:
        return 'Your cart page shows added items and totals. You can update quantities or remove items there.'

    if 'payment' in message_lower or 'checkout' in message_lower:
        return 'We support safe checkout and payment. Let me know if you want help with payment methods or order confirmation.'

    if 'product' in message_lower or 'item' in message_lower or 'find' in message_lower:
        products = _search_products(message_lower)
        if products:
            product_names = ', '.join(p['name'] for p in products)
            return f'I found these products: {product_names}. Ask for the price or details of one of them.'
        return 'Tell me the product name or category and I can help you find it in the catalog.'

    products = _search_products(message_lower)
    if products:
        product_names = ', '.join(p['name'] for p in products)
        return f'I found these products: {product_names}. Ask for the price or details of one of them.'

    return 'I can help with product search, cart questions, checkout, or account help. Try asking for a product by name or category.'
@chat_bp.route('/message', methods=['POST'])
@login_required
def chat_message():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Please type a question.'}), 400

    reply_text = generate_chat_response(user_message)
    return jsonify({'message': reply_text})

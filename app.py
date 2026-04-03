import os

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_session import Session
from redis import Redis

from database import init_db, get_db, close_db
from routes.auth import auth_bp
from routes.catalog import catalog_bp
from routes.cart import cart_bp
from routes.checkout import checkout_bp
from routes.payment import payment_bp
from routes.buyer import buyer_bp
from routes.seller import seller_bp
from routes.chat import chat_bp


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object('config.Config')

    redis_client = Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=0)
    app.config['SESSION_REDIS'] = redis_client
    Session(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        db = get_db()
        user_row = db.execute('SELECT id, username, role FROM users WHERE id = ?', (user_id,)).fetchone()
        if user_row:
            return User(user_row['id'], user_row['username'], user_row['role'])
        return None

    @app.teardown_appcontext
    def teardown_db(error=None):
        close_db(error)

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(chat_bp)

    init_db()

    @app.route('/')
    def index():
        from flask import render_template
        db = get_db()
        featured_products = db.execute('SELECT * FROM products LIMIT 8').fetchall()
        categories = db.execute('SELECT id, name FROM categories ORDER BY name').fetchall()
        return render_template('index.html', featured=featured_products, categories=categories)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5005)), debug=os.getenv('FLASK_DEBUG', '1') == '1')

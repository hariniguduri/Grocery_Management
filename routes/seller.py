from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from database import get_db
import os
from uuid import uuid4

seller_bp = Blueprint('seller', __name__, template_folder='templates/seller')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@seller_bp.route('/seller/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    db = get_db()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = float(request.form.get('price', '0'))
        stock = int(request.form.get('stock', '0'))
        category_id = request.form.get('category_id')
        
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_url = f"/uploads/{filename}"
        
        db.execute(
            'INSERT INTO products (name, description, price, stock, seller_id, image_url, category_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (name, description, price, stock, current_user.id, image_url, category_id if category_id else None)
        )
        db.commit()
        flash('Product added successfully.', 'success')
        return redirect(url_for('seller.dashboard'))

    products = db.execute('SELECT * FROM products WHERE seller_id = ?', (current_user.id,)).fetchall()
    categories = db.execute('SELECT id, name FROM categories ORDER BY name').fetchall()
    
    return render_template('seller/dashboard.html', products=products, categories=categories)

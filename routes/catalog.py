from flask import Blueprint, render_template, request, redirect, url_for, abort
from database import get_db

catalog_bp = Blueprint('catalog', __name__, template_folder='templates/catalog')


@catalog_bp.route('/catalog')
def catalog_index():
    db = get_db()
    q = request.args.get('q', '').strip()
    category = request.args.get('category')
    sort = request.args.get('sort', 'name')

    base_query = 'SELECT * FROM products'
    filters = []
    params = []

    if q:
        filters.append('(name LIKE ? OR description LIKE ?)')
        qparam = f'%{q}%'
        params.extend([qparam, qparam])

    if category:
        filters.append('category_id = ?')
        params.append(category)

    if filters:
        base_query += ' WHERE ' + ' AND '.join(filters)

    if sort == 'price_asc':
        base_query += ' ORDER BY price ASC'
    elif sort == 'price_desc':
        base_query += ' ORDER BY price DESC'
    elif sort == 'newest':
        base_query += ' ORDER BY created_at DESC'
    else:
        base_query += ' ORDER BY name ASC'

    products = db.execute(base_query, params).fetchall()
    categories = db.execute('SELECT id, name FROM categories').fetchall() if db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'").fetchone() else []

    return render_template(
        'catalog/index.html',
        products=products,
        categories=categories,
        search_query=q
    )


@catalog_bp.route('/category/<string:slug>')
def category_by_slug(slug):
    normalized = slug.strip().replace('-', ' ').lower()
    db = get_db()
    category_row = db.execute('SELECT id FROM categories WHERE lower(name) = ?', (normalized,)).fetchone()
    if not category_row:
        abort(404)
    return redirect(url_for('catalog.catalog_index', category=category_row['id']))


@catalog_bp.route('/<string:slug>')
def by_slug_root(slug):
    key = slug.strip().lower()
    if key == 'all':
        return redirect(url_for('catalog.catalog_index'))

    normalized = key.replace('-', ' ')
    db = get_db()
    category_row = db.execute('SELECT id FROM categories WHERE lower(name) = ?', (normalized,)).fetchone()
    if category_row:
        return redirect(url_for('catalog.catalog_index', category=category_row['id']))

    abort(404)


@catalog_bp.route('/catalog/<int:product_id>')
def detail(product_id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        return render_template('catalog/index.html', products=db.execute('SELECT * FROM products').fetchall())
    return render_template('catalog/detail.html', product=product)

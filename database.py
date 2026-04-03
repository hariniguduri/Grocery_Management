import sqlite3

from flask import g

from config import Config


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(Config.DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    with open('schema.sql', 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()
    
    # Seed default categories
    default_categories = [
        'Fruits',
        'Vegetables',
        'Dairy',
        'Grains',
        'Spices',
        'Beverages',
        'Snacks',
        'Frozen Foods'
    ]
    
    for category in default_categories:
        try:
            db.execute('INSERT INTO categories (name) VALUES (?)', (category,))
        except sqlite3.IntegrityError:
            pass  # Category already exists
    
    db.commit()
    db.close()

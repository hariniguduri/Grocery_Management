from database import get_db, init_db
from werkzeug.security import generate_password_hash

def seed():
    init_db()
    db = get_db()

    # Categories
    categories = ['Fruits', 'Vegetables', 'Dairy']
    for c in categories:
        db.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (c,))

    # Seller
    db.execute(
        '''INSERT OR IGNORE INTO users (username, email, password_hash, role)
           VALUES (?, ?, ?, ?)''',
        ('seller1', 'seller@test.com', generate_password_hash('1234'), 'seller')
    )

    # Buyer
    db.execute(
        '''INSERT OR IGNORE INTO users (username, email, password_hash, role)
           VALUES (?, ?, ?, ?)''',
        ('buyer1', 'buyer@test.com', generate_password_hash('1234'), 'buyer')
    )

    # Get seller id
    seller_id = db.execute(
        "SELECT id FROM users WHERE email='seller@test.com'"
    ).fetchone()['id']

    # Products
    products = [
        (seller_id, 'Apple', 80, 50),
        (seller_id, 'Milk', 50, 30),
        (seller_id, 'Rice', 120, 100)
    ]

    for p in products:
        db.execute(
            "INSERT INTO products (seller_id, name, price, stock) VALUES (?,?,?,?)",
            p
        )

    db.commit()
    db.close()
    print("Seed data added!")

if __name__ == "__main__":
    seed()
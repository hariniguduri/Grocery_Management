import json
from redis_client import r


def get_cart_key(user_id):
    return f"cart:{user_id}"


def add_to_cart(user_id, product_id, quantity, product_data):
    key = get_cart_key(user_id)
    existing = r.hget(key, str(product_id))

    if existing:
        item = json.loads(existing)
        item['quantity'] += quantity
    else:
        item = {
            "product_id": product_id,
            "name": product_data['name'],
            "price": product_data['price'],
            "quantity": quantity
        }

    r.hset(key, str(product_id), json.dumps(item))


def get_cart(user_id):
    key = get_cart_key(user_id)
    data = r.hgetall(key)

    items = []
    total = 0

    for v in data.values():
        item = json.loads(v)
        item['subtotal'] = item['price'] * item['quantity']
        total += item['subtotal']
        items.append(item)

    return {
        "items": items,
        "total": total
    }


def remove_from_cart(user_id, product_id):
    key = get_cart_key(user_id)
    r.hdel(key, str(product_id))


def clear_cart(user_id):
    key = get_cart_key(user_id)
    r.delete(key)
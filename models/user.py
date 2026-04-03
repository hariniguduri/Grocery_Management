from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id_, username, role='buyer', full_name=''):
        self.id = str(id_)
        self.username = username
        self.role = role
        self.full_name = full_name

    def is_seller(self):
        return self.role == 'seller'

    def is_buyer(self):
        return self.role == 'buyer'

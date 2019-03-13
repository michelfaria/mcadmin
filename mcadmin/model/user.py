# mcadmin/model/user.py

from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, user_id):
        super(User, self).__init__()
        self.user_id = user_id

    def get_id(self):
        return self.user_id

    @staticmethod
    def get(user_id):
        return User(user_id)

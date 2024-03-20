from flask_login import LoginManager, login_user,login_manager, UserMixin
from apps import login_manager
from apps.config import db

class User(UserMixin):
    def __init__(self, user_data):
        self.username = user_data["name"]
        self._id = user_data["_id"]
        self.email = user_data["email"]
        self.password = user_data["password"]
        self.role = user_data["role"]

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self._id
    
    def get_pass(self):
        return self.password
    
    def get_role(self):
        return self.role
    
    def __str__(self):
        return str(self)
    
@login_manager.user_loader
def load_user(user_id):
    user = db.users.find_one({'_id': user_id})
    if user is not None:
        return User(user)
    else:
        return None


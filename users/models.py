from mongoengine import Document, fields
from django.contrib.auth.hashers import make_password, check_password

class User(Document):
    username = fields.StringField(required=True, unique=True)
    email = fields.EmailField(required=True, unique=True)
    password = fields.StringField(required=True)
    name = fields.StringField(required=True)
    subjects = fields.ListField(fields.StringField(), default=['Computer Science'])
    theme = fields.StringField(default='light', choices=('light', 'dark'))
    avatar = fields.StringField(default='1')  # Default avatar
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    
    meta = {'collection': 'users'}
    
    @property
    def is_authenticated(self):
        return True
    
    def set_password(self, password):
        self.password = make_password(password)
    
    def check_password(self, password):
        return check_password(password, self.password)
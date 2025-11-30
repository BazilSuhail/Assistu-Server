from mongoengine import Document, fields, CASCADE
from users.models import User

class Note(Document):
    user = fields.ReferenceField(User, reverse_delete_rule=CASCADE)
    title = fields.StringField(required=True)
    transcript = fields.StringField()
    summary = fields.StringField()
    explanation = fields.ListField(fields.StringField(), default=[])  # Array of bullet 
    subject = fields.StringField(required=True)
    categories = fields.ListField(fields.StringField(), default=['General'])
    keywords = fields.ListField(fields.StringField(), default=[])
    importance = fields.StringField(default='medium', choices=('low', 'medium', 'high'))
    tags = fields.ListField(fields.StringField(), default=[])
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    
    meta = {'collection': 'notes'}
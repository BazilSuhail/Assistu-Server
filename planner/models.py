from mongoengine import Document, fields, CASCADE
from users.models import User

class StudyPlan(Document):
    user = fields.ReferenceField(
        User,
        required=True,
        reverse_delete_rule=CASCADE
    )
    title = fields.StringField(required=True, max_length=256)
    duration = fields.StringField(required=True)
    sessions = fields.ListField(
        fields.DictField()
    )
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    
    meta = {
        'collection': 'study_plans',
        'indexes': [
            {'fields': ['user']}
        ]
    }
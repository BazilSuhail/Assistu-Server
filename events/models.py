from mongoengine import Document, fields, CASCADE
from users.models import User
from tasks.models import Task

class Event(Document):
    user = fields.ReferenceField(User, reverse_delete_rule=CASCADE)
    title = fields.StringField(required=True)
    description = fields.StringField()
    event_type = fields.StringField(default='study_session', choices=('study_session', 'class', 'meeting', 'exam'))
    start_time = fields.DateTimeField(required=True)
    end_time = fields.DateTimeField(required=True)
    related_task = fields.ReferenceField(Task, null=True)
    created_at = fields.DateTimeField(auto_now_add=True)
    
    meta = {'collection': 'events'}
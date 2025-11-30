from mongoengine import Document, fields, CASCADE
from users.models import User

class Task(Document):
    user = fields.ReferenceField(User, reverse_delete_rule=CASCADE)
    title = fields.StringField(required=True)
    description = fields.StringField()
    subject = fields.StringField(required=True)
    type = fields.StringField(default='assignment', choices=('assignment', 'study', 'project', 'exam'))
    priority = fields.StringField(default='medium', choices=('low', 'medium', 'high'))
    status = fields.StringField(default='pending', choices=('pending', 'in_progress', 'completed', 'cancelled'))
    due_date = fields.DateTimeField(required=True)
    estimated_duration = fields.IntField(default=60)
    tags = fields.ListField(fields.StringField(), default=[])
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    completed_at = fields.DateTimeField(null=True)
    original_command = fields.StringField()

    meta = {'collection': 'tasks'}

# from mongoengine import Document, fields
# from users.models import User

# class Task(Document):
#     user = fields.ReferenceField(User, reverse_delete_rule=fields.CASCADE)
#     title = fields.StringField(required=True)
#     description = fields.StringField()
#     subject = fields.StringField(required=True)
#     type = fields.StringField(default='assignment', choices=('assignment', 'study', 'project', 'exam'))
#     priority = fields.StringField(default='medium', choices=('low', 'medium', 'high'))
#     status = fields.StringField(default='pending', choices=('pending', 'in_progress', 'completed', 'cancelled'))
#     due_date = fields.DateTimeField(required=True)
#     estimated_duration = fields.IntField(default=60)  # in minutes
#     tags = fields.ListField(fields.StringField(), default=[])
#     created_at = fields.DateTimeField(auto_now_add=True)
#     updated_at = fields.DateTimeField(auto_now=True)
#     completed_at = fields.DateTimeField(null=True)
#     original_command = fields.StringField()
    
#     meta = {'collection': 'tasks'}
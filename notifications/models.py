from mongoengine import Document, fields, EmbeddedDocument, CASCADE
from users.models import User

class RelatedEntity(EmbeddedDocument):
    type = fields.StringField(required=True)
    id = fields.StringField(required=True)

class Notification(Document):
    user = fields.ReferenceField(User, reverse_delete_rule=CASCADE)
    title = fields.StringField(required=True)
    message = fields.StringField(required=True)
    type = fields.StringField(default='task_reminder', choices=('task_reminder', 'event_reminder', 'system'))
    related_entity = fields.EmbeddedDocumentField(RelatedEntity, null=True)
    priority = fields.StringField(default='medium', choices=('low', 'medium', 'high'))
    scheduled_for = fields.DateTimeField(required=True)
    created_at = fields.DateTimeField(auto_now_add=True)
    
    meta = {'collection': 'notifications'}
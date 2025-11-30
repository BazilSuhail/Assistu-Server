from users.models import User

class MongoEngineBackend:
    def authenticate(self, request, email=None, password=None):
        user = User.objects(email=email).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        return User.objects(id=user_id).first()
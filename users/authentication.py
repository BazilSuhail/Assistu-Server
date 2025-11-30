# users/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from bson import ObjectId
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import logging

logger = logging.getLogger(__name__)

class MongoEngineJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Instead of receiving user_id directly, we receive the validated token
        and extract user_id from it, then fetch the user.
        """
        try:
            # Extract user_id from the validated token
            user_id = validated_token.get('user_id')
            print(f"Extracted user_id from token: {user_id}")
            
            if not user_id:
                raise AuthenticationFailed('User ID not found in token.')
            
            # Convert to ObjectId and find user
            if isinstance(user_id, str):
                user = User.objects(id=ObjectId(user_id)).first()
            else:
                user = User.objects(id=ObjectId(str(user_id))).first()
                
            if user is None:
                print(f"User not found with ID: {user_id}")
                raise AuthenticationFailed('User not found.')
                
            print(f"Found user: {user}")
            return user
            
        except Exception as e:
            print(f"Exception in get_user: {e}")
            raise AuthenticationFailed('User not found.')
# # users/authentication.py
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from bson import ObjectId
# from .models import User  # Your MongoEngine User model

# class MongoEngineJWTAuthentication(JWTAuthentication):
#     """
#     JWT Authentication class compatible with MongoEngine.
#     Overrides get_user to fetch MongoEngine User by ObjectId.
#     """

#     def get_user(self, user_id):
#         """
#         Return MongoEngine User instance from JWT user_id.
#         """
#         try:
#             # Convert string ID from token to ObjectId
#             return User.objects(id=ObjectId(user_id)).first()
#         except Exception:
#             return None

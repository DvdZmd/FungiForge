from authlib.oauth2.rfc6749 import grants
from database.models import User
from auth.models import OAuth2Token

class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user

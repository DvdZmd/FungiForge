from database.models import db
from authlib.oauth2.rfc6749 import TokenMixin
from authlib.integrations.sqla_oauth2 import OAuth2ClientMixin

class OAuth2Client(db.Model, OAuth2ClientMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class OAuth2Token(db.Model, TokenMixin):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(48), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    access_token = db.Column(db.String(255), unique=True, nullable=False)
    refresh_token = db.Column(db.String(255), unique=True)
    issued_at = db.Column(db.Integer, nullable=False)
    expires_in = db.Column(db.Integer, nullable=False)
    scope = db.Column(db.String(128))
    revoked = db.Column(db.Boolean, default=False)

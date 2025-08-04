from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from werkzeug.security import gen_salt
from datetime import datetime, timedelta
from database.models import db, User
from auth.models import OAuth2Client, OAuth2Token

authorization = AuthorizationServer()

def query_client(client_id):
    return OAuth2Client.query.filter_by(client_id=client_id).first()

def save_token(token, request):
    toks = OAuth2Token.query.filter_by(
        client_id=request.client.client_id,
        user_id=request.user.id
    )
    # Revoke existing tokens
    for t in toks:
        db.session.delete(t)
    new_token = OAuth2Token(
        client_id=request.client.client_id,
        user_id=request.user.id,
        **token
    )
    db.session.add(new_token)
    db.session.commit()

def config_oauth(app):
    from auth.grants import PasswordGrant  # see below
    authorization.init_app(app, query_client=query_client, save_token=save_token)
    authorization.register_grant(PasswordGrant)

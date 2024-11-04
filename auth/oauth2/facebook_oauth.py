import requests
from urllib.parse import urlencode
from flask import Flask, redirect, request, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from backend.src.models.user_model import User
from backend.src.utils.jwt_util import create_jwt_token
from backend.src.config.env_config import FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET, FACEBOOK_REDIRECT_URI, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# OAuth configuration
oauth = OAuth(app)
facebook = oauth.register(
    name='facebook',
    client_id=FACEBOOK_CLIENT_ID,
    client_secret=FACEBOOK_CLIENT_SECRET,
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    authorize_params=None,
    authorize_token_params=None,
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=FACEBOOK_REDIRECT_URI,
    client_kwargs={'scope': 'email'}
)

@app.route('/auth/facebook/login')
def facebook_login():
    redirect_uri = url_for('facebook_callback', _external=True)
    return facebook.authorize_redirect(redirect_uri)

@app.route('/auth/facebook/callback')
def facebook_callback():
    try:
        token = facebook.authorize_access_token()
        user_info = facebook.get('https://graph.facebook.com/me?fields=id,name,email').json()
        user = get_or_create_user(user_info)
        jwt_token = create_jwt_token(user)
        session['jwt_token'] = jwt_token
        return redirect(url_for('dashboard'))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_or_create_user(user_info):
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(
            facebook_id=user_info['id'],
            email=user_info['email'],
            name=user_info['name']
        )
        user.save()
    return user

@app.route('/auth/facebook/logout')
def facebook_logout():
    session.pop('jwt_token', None)
    return redirect(url_for('index'))

def facebook_get_auth_url():
    params = {
        'client_id': FACEBOOK_CLIENT_ID,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
        'state': 'random_state_string',
        'scope': 'email',
        'response_type': 'code'
    }
    url = 'https://www.facebook.com/v11.0/dialog/oauth?' + urlencode(params)
    return url

def facebook_get_access_token(code):
    token_url = 'https://graph.facebook.com/v11.0/oauth/access_token'
    params = {
        'client_id': FACEBOOK_CLIENT_ID,
        'client_secret': FACEBOOK_CLIENT_SECRET,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
        'code': code
    }
    response = requests.get(token_url, params=params)
    token_data = response.json()
    return token_data['access_token']

def facebook_get_user_profile(access_token):
    profile_url = 'https://graph.facebook.com/me?fields=id,name,email'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(profile_url, headers=headers)
    return response.json()

@app.route('/auth/facebook/authorize')
def facebook_authorize():
    auth_url = facebook_get_auth_url()
    return redirect(auth_url)

@app.route('/auth/facebook/authorized')
def facebook_authorized():
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({'error': 'Authorization code not found.'}), 400

        access_token = facebook_get_access_token(code)
        user_info = facebook_get_user_profile(access_token)

        user = get_or_create_user(user_info)
        jwt_token = create_jwt_token(user)
        session['jwt_token'] = jwt_token

        return redirect(url_for('dashboard'))

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Utility Functions for Facebook OAuth2.0

def build_oauth_url(base_url, client_id, redirect_uri, state, scope):
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
        'scope': scope,
        'response_type': 'code'
    }
    return f"{base_url}?{urlencode(params)}"

def exchange_code_for_token(code):
    token_url = 'https://graph.facebook.com/v11.0/oauth/access_token'
    params = {
        'client_id': FACEBOOK_CLIENT_ID,
        'client_secret': FACEBOOK_CLIENT_SECRET,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
        'code': code
    }
    response = requests.get(token_url, params=params)
    return response.json()

def handle_oauth_response(response):
    if response.status_code != 200:
        raise Exception('Error fetching data from Facebook')
    return response.json()

def save_facebook_user_data(facebook_data):
    user = User.query.filter_by(facebook_id=facebook_data['id']).first()
    if not user:
        user = User(
            facebook_id=facebook_data['id'],
            name=facebook_data['name'],
            email=facebook_data['email']
        )
        user.save()
    return user

def generate_jwt_for_user(user):
    return create_jwt_token(user)

@app.route('/auth/facebook/revoke')
def revoke_facebook_token():
    try:
        jwt_token = session.get('jwt_token')
        if jwt_token:
            session.pop('jwt_token')
            return jsonify({'message': 'Facebook session revoked successfully'}), 200
        else:
            return jsonify({'error': 'No session found to revoke.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
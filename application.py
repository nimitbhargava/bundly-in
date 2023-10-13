from flask import Flask, render_template, request, redirect, url_for, session as login_session
from sqlalchemy import create_engine
from database_setup import Base, User, Bundle, Links
from sqlalchemy.orm import sessionmaker
import string, random
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Constants
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
DATABASE_URL = 'sqlite:///bundly.db'

# Connect to database bundly.db
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Helper Functions

def generate_state():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

def is_creator(bundle):
    creator = session.query(Bundle).filter_by(id=bundle.id).first().creator
    return login_session['email'] == creator if 'email' in login_session else False

def get_bundle(bundle_id):
    return session.query(Bundle).filter(Bundle.id == bundle_id).first()

def get_links(bundle_id):
    return session.query(Links).filter(Links.bundle_id == bundle_id).all()

# Routes

@app.route('/')
def home():
    bundles = session.query(Bundle).all()
    return render_template('home.html', bundles=bundles)

@app.route('/<int:bundle_id>')
def show_bundle(bundle_id):
    bundle = get_bundle(bundle_id)
    if bundle is None:
        return render_template('home.html')
    links = get_links(bundle_id)
    is_owner = is_creator(bundle)
    return render_template('show_bundle.html', is_creator=is_owner, links=links, bundle=bundle)

@app.route('/add-link/<int:bundle_id>', methods=['POST'])
def add_link(bundle_id):
    if 'username' not in login_session:
        return redirect('/login')
    bundle = get_bundle(bundle_id)
    is_owner = is_creator(bundle)
    if not is_owner:
        return "You don't seem to be the owner"
    new_url = Links(url=request.form["input-add-url"], bundle_id=bundle_id)
    session.add(new_url)
    session.commit()
    return redirect(url_for('show_bundle', bundle_id=bundle_id))

@app.route('/<int:bundle_id>/delete', methods=['POST'])
def remove_link(bundle_id):
    link_id = request.form['link_id']
    link = session.query(Links).filter_by(id=link_id).first()
    if link is None:
        return "Incorrect request"
    session.delete(link)
    session.commit()
    return url_for('show_bundle', bundle_id=bundle_id)
# Login
@app.route('/login')
def login():
    # Create anti-forgery state token to prevent request forgery
    # Store it in the session for later validation
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, client_id=CLIENT_ID)


# Logout
@app.route('/login')
def logout():
    return "Logout Page"


# Google Login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate Anti-Forgery State Token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()

    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print
        "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output


# Google Logout
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET requests to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('home'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.secret_key = 'ultra_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)




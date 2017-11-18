from flask import Flask, render_template, request, redirect, url_for, session as login_session
from sqlalchemy import create_engine
from database_setup import Base, User, Bundle, Links
from sqlalchemy.orm import sessionmaker
import json
import string, random
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

# Connect to database bundly.db
engine = create_engine('sqlite:///bundly.db')
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Home Page
@app.route('/')
def home():
    bundles = session.query(Bundle).all()
    return render_template('home.html', bundles=bundles)


# View Bundle
@app.route('/<int:bundle_id>')
def show_bundle(bundle_id):
    bundle = session.query(Bundle).filter(Bundle.id == bundle_id).first()
    if bundle is None:
        return render_template('home.html')
    links = session.query(Links).filter(Links.bundle_id == bundle_id).all()
    return render_template('show_bundle.html', links=links, bundle=bundle)


# Operations on Links
# Add Link
@app.route('/add-link/<int:bundle_id>', methods=['POST'])
def add_link(bundle_id):
    new_url = Links(url=request.form["input-add-url"], bundle_id=bundle_id)
    session.add(new_url)
    session.commit()
    return redirect(url_for('show_bundle', bundle_id=bundle_id))


# Remove Link
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
@app.route('/gconnect')
def gconnect():
    return "gconnect"


# Google Logout
@app.route('/gdisconnect')
def gdisconnect():
    return "g disconnect Page"


if __name__ == '__main__':
    app.secret_key = 'ultra_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

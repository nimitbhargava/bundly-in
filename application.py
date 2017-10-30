from flask import Flask, render_template
from sqlalchemy import create_engine
from database_setup import Base, User, Bundle, Links
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Connect to database bundly.db
engine = create_engine('sqlite:///bundly.db')
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Home Page
@app.route('/')
def home():
    return render_template('home.html')


# View Bundle
@app.route('/<int:bundle_id>')
def show_bundle(bundle_id):
    bundle = session.query(Bundle).filter(Bundle.id==bundle_id).first()
    if bundle is None:
        return render_template('home.html')
    links = session.query(Links).filter(Links.bundle_id==bundle_id).all()
    return render_template('show_bundle.html', links = links, bundle = bundle)


# Login
@app.route('/login')
def login():
    return "Login Page"


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
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
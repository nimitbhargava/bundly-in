from flask import Flask
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
def show_info():
    return "Welcome to Bundly.in"


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
from flask import Flask

app = Flask(__name__)


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
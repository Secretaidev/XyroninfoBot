from flask import Flask
app = Flask(__name__)

@app.route('/')
def health():
    return 'OK', 200

@app.route('/health')
def check():
    return 'OK', 200

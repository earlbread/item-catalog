"""Server code for item-catalog app
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def test():
    return "Hello?"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

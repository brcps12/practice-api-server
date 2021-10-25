from flask import Flask
from math import ceil

app = Flask("api_test")

@app.route('/')
def hello():
    return 'Hello World'

if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=True)

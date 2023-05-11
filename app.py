from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/super_simple')
def super_super():
    return 'Hello from planetary Api.'


if __name__ == '__main__':
    app.run()

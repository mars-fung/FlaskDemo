from flask import Flask,url_for,redirect

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('http://127.0.0.1:5000/index')


@app.route('/index')
def hello_world():
    return 'index.html, Hello World!'

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' % name

@app.route('/url/<username>')
def url(username) : pass

with app.test_request_context():
    print (url_for('url',username='fengjm'))

if __name__ == '__main__':
    app.run()


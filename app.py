from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '''<h1>Welcome to the ECS-powered Flask Application!</h1>
              <p>This application is running successfully on AWS ECS. <br>
              Docker and ECS are seamlessly powering this Hello World app.</p>'''

@app.route('/health')
def health():
    return 'Server is up and running on AWS ECS'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7881)

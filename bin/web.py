from flask import Flask
import os
app = Flask(__name__)

content = "Hello World " + os.environ["service_nr"]

@app.route('/')
def hello():
    return content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ["port"])

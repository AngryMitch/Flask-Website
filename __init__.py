from flask import Flask, render_template, Response

app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
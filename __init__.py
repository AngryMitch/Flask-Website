from flask import Flask
import views

app = Flask(__name__)
app.register_blueprint(views.mainBP)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
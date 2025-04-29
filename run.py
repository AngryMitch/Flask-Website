# Entry Point to Our Application - Mitch
from riffhub import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
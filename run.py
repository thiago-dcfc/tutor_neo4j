from tutor import app
import os

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(port=5000)

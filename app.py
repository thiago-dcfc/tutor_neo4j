from tutor import app
from commands import seeds_blueprint

app.register_blueprint(seeds_blueprint)

if __name__ == "__main__":
    app.run(port=5000)

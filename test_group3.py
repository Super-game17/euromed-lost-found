from flask import Flask
from app.routes.group3_search import group3_search
import webbrowser
from threading import Timer

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

app.register_blueprint(group3_search)


def open_browser():
    webbrowser.open("http://127.0.0.1:5000/search")


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=True)
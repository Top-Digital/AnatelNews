from flask import Flask
from api import api_bp
from anatel_news import collect_and_post_news

app = Flask(__name__)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

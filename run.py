# run.py
import datetime
from flask import Flask
from app.extensions import init_app
from flask_cors import CORS
from app.auth.routes import init_auth_routes
from app.profile.routes import init_profile_routes

app = Flask(__name__)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=60)

# Initialize app with extensions and routes
init_app(app)
init_auth_routes(app)
init_profile_routes(app)

CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(debug=True)

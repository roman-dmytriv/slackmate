import os

from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

from app.api.channels import slack_api_bp
from app.auth.oauth import slack_auth_bp
from app.config import Config

app = Flask(__name__)


@app.route('/swagger.json', methods=['GET'])
def swagger_json():
    return send_from_directory(os.getcwd(), 'swagger.json')


# Define Swagger UI blueprint
SWAGGER_URL = '/api/docs'  # noqa URL for accessing Swagger UI (http://localhost:5000/api/docs)
API_URL = '/swagger.json'   # noqa URL for accessing the Swagger JSON (http://localhost:5000/swagger.json)
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Slack API"  # Swagger UI configuration
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Set the secret key
app.secret_key = Config.SECRET_KEY

# Register the Slack auth blueprint
app.register_blueprint(slack_auth_bp)
app.register_blueprint(slack_api_bp, url_prefix='/api/slack')

if __name__ == "__main__":
    app.run(debug=True, port=5000)

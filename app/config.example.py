# app/config.py

import secrets


class Config:
    # Slack OAuth configuration
    SLACK_CLIENT_ID = '<your_slack_client_id>'
    SLACK_CLIENT_SECRET = '<your_slack_secret>'
    SLACK_API_TOKEN = '<your_api_token>'
    SLACK_TEAM_ID = "<your_team_id>"

    # Secret key configuration
    SECRET_KEY = secrets.token_hex(16)

    # Enable CSRF protection
    CSRF_ENABLED = True

    # Specify HTTP methods for CSRF protection
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

import os
from flask import Blueprint, redirect, request, jsonify, make_response, session
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse
from slack_sdk.oauth.installation_store.models import Installation
from slack_sdk import WebClient
from app.config import Config

# Define the blueprint for the Slack authentication routes
slack_auth_bp = Blueprint('auth', __name__)

# Initialize Installation Store
installation_store = FileInstallationStore()

# Slack OAuth 2.0 Redirect URL
oauth_redirect_url = "https://581b-45-12-26-219.ngrok-free.app/auth/callback"

# Initialize Slack WebClient with the Slack API token from the configuration
slack_client = WebClient(token=Config.SLACK_API_TOKEN)


@slack_auth_bp.route('/auth/authorize', methods=['GET'])
def slack_auth():
    # Generate a random state and store it in the session
    state = os.urandom(16).hex()
    session['slack_auth_state'] = state

    authorize_url_generator = AuthorizeUrlGenerator(
        client_id=Config.SLACK_CLIENT_ID,
        scopes=["channels:read", "chat:write", "users:read"],
        redirect_uri=oauth_redirect_url,
    )
    authorization_url = authorize_url_generator.generate(state=state)
    return redirect(authorization_url)


@slack_auth_bp.route('/auth/callback', methods=['GET'])
def slack_auth_callback():
    try:
        # Verify state to prevent CSRF attacks
        state = session.pop('slack_auth_state', None)
        if state is None or state != request.args.get('state'):
            return make_response(
                jsonify({"error": "Invalid state parameter."}), 400)

        # Verify and exchange authorization code for access token
        auth_result = slack_client.oauth_v2_access(
            client_id=Config.SLACK_CLIENT_ID,
            client_secret=Config.SLACK_CLIENT_SECRET,
            code=request.args.get('code')
        )

        if auth_result is None:
            return make_response(jsonify({
                "error": "Authentication failed: No response from Slack API."
            }), 500)

        if isinstance(auth_result, SlackResponse) and auth_result["ok"]:
            # Store the installation data (access token, bot user ID, etc.)
            installation = Installation(
                team_id=auth_result['team']['id'],
                user_id=auth_result['authed_user']['id'],
                bot_token=auth_result['access_token'],
            )
            installation_store.save(installation)

            # Respond with a success message
            return make_response(jsonify({
                "message": "Authentication successful! You can now use the Slack API."  # noqa
            }), 200)

        elif isinstance(auth_result, dict) and 'error' in auth_result:
            return make_response(jsonify({
                "error": f"Authentication failed: {auth_result['error']}"
            }), 500)

        else:
            return make_response(jsonify({
                "error": "Authentication failed: Unexpected response from Slack API."   # noqa
            }), 500)

    except SlackApiError as e:
        # Handle Slack API errors
        error_message = e.response['error']
        return make_response(jsonify({
            "error": f"Slack API Error: {error_message}"
        }), 500)

    except Exception as e:
        return make_response(jsonify({
            "error": f"Internal Server Error: {str(e)}"
        }), 500)

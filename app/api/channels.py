import logging

import requests
from flask import Blueprint, jsonify, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.oauth.installation_store import FileInstallationStore

from app.config import Config

log = logging.getLogger(__name__)

slack_client = WebClient(token=Config.SLACK_API_TOKEN)
slack_api_bp = Blueprint('slack_api', __name__)

installation_store = FileInstallationStore()

SLACK_API_URL = 'https://www.slack.com/api/chat.postMessage'
JSON_CONTENT_TYPE = 'application/json; charset=utf-8'


@slack_api_bp.route('/users', methods=['GET'])
def get_slack_users():
    try:
        installation = get_installation()
        access_token = installation.bot_token
        response = slack_client.users_list(token=access_token)
        if response.get('ok'):
            basic_user_info = []
            for member in response['members']:
                basic_user_info.append({
                    'id': member['id'],
                    'name': member['name'],
                    'real_name': member['real_name'],
                    'team_id': member['team_id']
                })
            return jsonify(basic_user_info)
        else:
            return jsonify({
                "error": "Failed to retrieve user list from Slack API."
            }), 500
    except SlackApiError as e:
        log.exception("Slack API Error occurred while retrieving users")
        return jsonify({
            "error": f"Slack API Error: {e.response['error']}"
        }), 500
    except Exception:
        log.exception("Failed to retrieve Slack users")
        return jsonify({"error": "Failed to retrieve Slack users."}), 500


@slack_api_bp.route('/send_message', methods=['POST'])
def send_message():
    try:
        channel_id = request.json.get('channel_id')
        message_text = request.json.get('message_text')

        if not channel_id or not message_text:
            return jsonify({
                "error": "Channel ID and message text are required."
            }), 400

        payload = {'channel': channel_id, 'text': message_text}
        installation = get_installation()
        headers = {
            'Authorization': f'Bearer {installation.bot_token}',
            "Content-Type": JSON_CONTENT_TYPE
        }

        response = requests.post(SLACK_API_URL, json=payload, headers=headers)

        if response.ok:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "Failed to send message"
            }), response.status_code

    except SlackApiError as e:
        log.exception("Slack API Error occurred while sending message")
        return jsonify({
            "error": f"Slack API Error: {e.response['error']}"
        }), 500
    except Exception as e:
        log.exception("Failed to send Slack message")
        return jsonify({
            "error": f"Failed to send Slack message: {str(e)}"
        }), 500


def get_installation():
    return installation_store.find_installation(
        enterprise_id=None,
        team_id=Config.SLACK_TEAM_ID,
    )

import pytest
from flask import Flask
from slack_mate.app.auth.oauth import slack_auth_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(slack_auth_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_slack_auth_redirect(client):
    response = client.get('/auth/authorize')
    assert response.status_code == 302  # Expecting a redirect


def test_slack_auth_callback_invalid_state(client):
    with client.session_transaction() as sess:
        sess['slack_auth_state'] = 'valid_state'
    response = client.get('/auth/callback?code=test_code&state=invalid_state')
    assert response.status_code == 400


def test_slack_auth_callback_no_state(client):
    response = client.get('/auth/callback?code=test_code')
    assert response.status_code == 400


def test_slack_auth_callback_successful_auth(client, monkeypatch):
    # Define a mock response from the Slack API
    mock_auth_result = {
        "ok": True,
        "team": {"id": "team_id"},
        "authed_user": {"id": "user_id"},
        "access_token": "access_token"
    }

    # Mock the OAuth v2 access function to return the mock response
    def mock_oauth_v2_access(*args, **kwargs):
        return mock_auth_result
    monkeypatch.setattr(
        'slack_mate.app.auth.oauth.slack_client.oauth_v2_access',
        mock_oauth_v2_access
    )

    # Set the expected state in the session
    with client.session_transaction() as sess:
        sess['slack_auth_state'] = 'valid_state'

    # Make a GET request to the authentication callback route
    response = client.get('/auth/callback?code=test_code&state=valid_state')

    # Verify the response status code
    assert response.status_code == 200

    # Verify that the authentication
    # was successful message is present in the response
    assert b"Authentication successful!" in response.data


def test_slack_auth_callback_oauth_error(client, monkeypatch):
    def mock_oauth_v2_access(*args, **kwargs):
        return {
            "ok": False,
            "error": "invalid_auth"
        }
    monkeypatch.setattr(
        'slack_mate.app.auth.oauth.slack_client.oauth_v2_access',
        mock_oauth_v2_access
    )

    with client.session_transaction() as sess:
        sess['slack_auth_state'] = 'valid_state'
    response = client.get('/auth/callback?code=test_code&state=valid_state')
    assert response.status_code == 500
    assert b"Authentication failed: invalid_auth" in response.data


def test_slack_auth_callback_no_response(client, monkeypatch):
    def mock_oauth_v2_access(*args, **kwargs):
        return None
    monkeypatch.setattr(
        'slack_mate.app.auth.oauth.slack_client.oauth_v2_access',
        mock_oauth_v2_access
    )

    with client.session_transaction() as sess:
        sess['slack_auth_state'] = 'valid_state'
    response = client.get('/auth/callback?code=test_code&state=valid_state')
    assert response.status_code == 500
    assert b"Authentication failed: No response from Slack API." in response.data   # noqa

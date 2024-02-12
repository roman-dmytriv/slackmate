import pytest
import json
from unittest.mock import patch
from flask import Flask
from slack_mate.app.api.channels import slack_api_bp


@pytest.fixture
def client():
    # Create a test Flask app
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(slack_api_bp)
    with app.test_client() as client:
        yield client


class MockResponse:
    def __init__(self, json_data, status_code, ok):
        self._json_data = json_data
        self.status_code = status_code
        self.ok = ok

    def json(self):
        return self._json_data


def test_get_slack_users_success(client):
    # Mocking the WebClient and its users_list method
    with patch(
        'slack_mate.app.api.channels.slack_client.users_list'
    ) as mock_users_list:
        # Mocking a successful response from the Slack API
        mock_users_list.return_value = {
            'ok': True,
            'members': [{
                'id': '123',
                'name': 'user1',
                'real_name': 'User One',
                'team_id': 'team1',
            }]
        }

        # Sending a GET request to the endpoint
        response = client.get('/users')

        # Checking if the response status code is 200
        assert response.status_code == 200

        # Checking if the response contains the expected user information
        expected_response = [{
            'id': '123',
            'name': 'user1',
            'real_name': 'User One',
            'team_id': 'team1',
        }]
        assert json.loads(response.data) == expected_response


def test_get_slack_users_failure(client):
    # Mocking the WebClient and its users_list method to simulate a failure
    with patch(
        'slack_mate.app.api.channels.slack_client.users_list'
    ) as mock_users_list:
        # Mocking a failure response from the Slack API
        mock_users_list.return_value = {
            'ok': False, 'error': 'Error retrieving user list'}

        # Sending a GET request to the endpoint
        response = client.get('/users')

        # Checking if the response status code is 500
        assert response.status_code == 500

        # Checking if the response contains the expected error message
        expected_response = {
            'error': 'Failed to retrieve user list from Slack API.'}
        assert json.loads(response.data) == expected_response


def test_send_message_success(client):
    # Mocking the requests.post method
    with patch('slack_mate.app.api.channels.requests.post') as mock_post:
        # Mocking a successful response from the Slack API
        mock_response = MockResponse({
            'message': 'Message sent successfully'}, 200, True)
        mock_post.return_value = mock_response

        # Sending a POST request to the endpoint
        payload = {'channel_id': 'channel1', 'message_text': 'Hello World!'}
        response = client.post('/send_message', json=payload)

        print(json.loads(response.data))

        # Checking if the response status code is 200
        assert response.status_code == 200

        # Checking if the response contains the expected message
        expected_response = {'message': 'Message sent successfully'}
        assert json.loads(response.data) == expected_response


def test_send_message_failure(client):
    # Mocking the requests.post method to simulate a failure
    with patch('slack_mate.app.api.channels.requests.post') as mock_post:
        # Mocking a failure response from the Slack API
        mock_response = MockResponse({
            'error': 'Failed to send message'}, 500, False)
        mock_post.return_value = mock_response

        # Sending a POST request to the endpoint
        payload = {'channel_id': 'channel1', 'message_text': 'Hello World!'}
        response = client.post('/send_message', json=payload)

        print(json.loads(response.data))

        # Checking if the response status code is 500
        assert response.status_code == 500

        # Checking if the response contains the expected error message
        expected_response = {'error': 'Failed to send message'}
        assert json.loads(response.data) == expected_response


if __name__ == '__main__':
    pytest.main()

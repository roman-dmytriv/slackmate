# Slack Mate App

Slack Mate is a Flask-based application that integrates with the Slack API to perform various tasks such as retrieving user information and sending messages.

## Prerequisites

Before running the Slack Mate app, ensure you have the following dependencies installed:

- Flask==3.0.2
- flask-swagger-ui==4.11.1
- requests==2.31.0
- slack_sdk==3.26.2
- Flask-WTF==1.2.1

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/roman-dmytriv/slackmate.git

2. **Navigate to the project directory:**

    ```bash
    cd slack_mate

3. **Istall dependencies using pip:**

    ```bash
    pip install -r requirements.txt

## Configuration

1. Rename the `config.example.py` file to `config.py`.
2. Fill in your Slack API token, client ID, client secret, and other necessary configurations in the `config.py` file.

## Slack Authentication

To authenticate with Slack and obtain access to the Slack API, follow these steps:  

1. Navigate to `http://localhost:5000/auth/authorize` to initiate the authentication process.
2. You will be redirected to Slack's authorization page where you will be prompted to grant access to the Slack Mate app.
3. After granting access, you will be redirected back to the Slack Mate app.
4. Upon successful authentication, you will receive a confirmation message indicating that authentication was successful.

## Running the App

To run the Slack Mate app, execute the following command: `python run.py`

The app will start running on `http://localhost:5000` by default.

## Endpoints

- `/api/slack/users`: Retrieves basic information about Slack users.
- `/api/slack/send_message`: Sends a message to a specified channel on Slack.

## Usage

- Navigate to <http://localhost:5000/api/slack/users> to retrieve user information.
- Use the /api/slack/send_message endpoint to send a message. Make a POST request with the following JSON payload:

    ```json
    {
    "channel_id": "your_channel_id",
    "message_text": "Your message text here"
    }

Replace `"your_channel_id"` with the ID of the channel you want to send the message to, and `"Your message text here"` with the text of the message you want to send.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue if you encounter any bugs or have suggestions for improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

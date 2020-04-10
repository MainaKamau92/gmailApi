from flask import Flask
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
creds = None


def authorize():
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service


@app.route("/")
def index():
    service = authorize()

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

    return {"labels": labels}


@app.route('/threads')
def get_threads():
    service = authorize()
    response = service.users().threads().list(userId="me", q="quincy@freecodecamp.org").execute()
    threads = []
    if 'threads' in response:
        threads.extend(response['threads'])

    return {"messages": threads}


@app.route('/messages')
def get_messages():
    service = authorize()
    response = service.users().messages().list(userId="me").execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    details = [service.users().messages().get(userId="me", id=i["id"]).execute() for i in messages[:6]]
    return {"messages": details}


@app.route('/profile')
def get_profile():
    service = authorize()
    profile = service.users().getProfile(userId="me").execute()
    return {"profile": profile}


if __name__ == "__main__":
    app.run()

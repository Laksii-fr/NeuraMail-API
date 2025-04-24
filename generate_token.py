import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define the OAuth 2.0 Scopes
SCOPES = ['https://mail.google.com/']

def get_oauth2_token():
    creds = None
    token_pickle = 'token.pickle'

    # Load existing credentials if available
    if os.path.exists(token_pickle):
        with open(token_pickle, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, or the token has expired, perform login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Automatically opens the consent screen

        # Save the credentials to a file
        with open(token_pickle, 'wb') as token:
            pickle.dump(creds, token)

    return creds

if __name__ == '__main__':
    get_oauth2_token()
    print("Token generated and saved as 'token.pickle'")
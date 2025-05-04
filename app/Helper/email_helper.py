# app/helper/email_helper.py
import time
import base64
import pickle
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import email
from email.header import decode_header
from app.Helper.api_helper import extract_content_from_json, create_chat
import app.utils.mongo_utils as mongo
import json
import os
from email_reply_parser import EmailReplyParser

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_IMAP = os.getenv("EMAIL_IMAP")
SCOPES = ['https://mail.google.com/']



def create_processed_folder(mail):
    try:
        mail.create("Processed")
    except:
        pass

def search_emails(mail, keyword=None):
    query = f'(UNSEEN SUBJECT "{keyword}")' if keyword else '(UNSEEN)'
    status, messages = mail.search(None, query)
    return status, messages

# def parse_email_from_bytes(response_part):
#     msg = email.message_from_bytes(response_part[1])

#     # Decode Subject
#     subject, encoding = decode_header(msg["Subject"])[0]
#     subject = subject.decode(encoding or 'utf-8') if isinstance(subject, bytes) else subject

#     # Decode From
#     from_, encoding = decode_header(msg.get("From"))[0]
#     from_ = from_.decode(encoding or 'utf-8') if isinstance(from_, bytes) else from_

#     # Headers for threading
#     message_id = msg.get("Message-ID")
#     in_reply_to = msg.get("In-Reply-To")
#     references = msg.get("References")

#     # Extract body
#     body = ""
#     if msg.is_multipart():
#         for part in msg.walk():
#             if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
#                 body_bytes = part.get_payload(decode=True)
#                 if body_bytes:
#                     body += decode_body(body_bytes)
#                     break
#     else:
#         body_bytes = msg.get_payload(decode=True)
#         if body_bytes:
#             body += decode_body(body_bytes)
        
#         cleaned_body = clean_body(body.strip())
#         parsed_reply = EmailReplyParser.parse_reply(cleaned_body)
        
#         return {
#             "subject": subject,
#             "from": from_,
#             "message_id": message_id,
#             "in_reply_to": in_reply_to,
#             "references": references,
#             "body": parsed_reply if parsed_reply else cleaned_body
#         }
#=============================================================================================================================
def parse_email_from_bytes(response_part):
    msg = email.message_from_bytes(response_part[1])
    subject, encoding = decode_header(msg["Subject"])[0]
    subject = subject.decode(encoding or 'utf-8') if isinstance(subject, bytes) else subject

    from_, encoding = decode_header(msg.get("From"))[0]
    from_ = from_.decode(encoding or 'utf-8') if isinstance(from_, bytes) else from_
    message_id = msg.get("Message-ID")
    in_reply_to = msg.get("In-Reply-To")
    references = msg.get("References")

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                body_bytes = part.get_payload(decode=True)
                if body_bytes:
                    body += decode_body(body_bytes)
                    break
    else:
        body_bytes = msg.get_payload(decode=True)
        if body_bytes:
            body += decode_body(body_bytes)
    cleaned_body = clean_body(body.strip())
    parsed_reply = EmailReplyParser.parse_reply(cleaned_body)
    return {
        "subject": subject,
        "from": from_,
        "message_id": message_id,
        "in_reply_to": in_reply_to,
        "references": references,
        "body": parsed_reply if parsed_reply else cleaned_body
    }
#=============================================================================================================================

def handle_email_processing(emails, user_id):
    result = []
    getdata = extract_content_from_json(emails)
    for email_data in getdata:
        body = {
            "Sender": email_data['sender'],
            "Subject": email_data['subject'],
            "Email": email_data['body']
        }
        response = create_chat(body, user_id)
        data = json.loads(response[0]['message'])
        result.append(data)
        # mongo.save_data(data, body)
    return result

def mark_as_processed(mail, num):
    if mail.copy(num, 'Processed')[0] == 'OK':
        mail.store(num, '+FLAGS', '\\Deleted')
    else:
        print(f"Failed to copy email {num} to Processed folder")

def mark_unread(mail, num):
    mail.store(num, '-FLAGS', '\\Seen')

# ========================== AUTHENTICATION ============================= #
def get_oauth2_token():
    creds = None
    token_pickle = 'token.pickle'
    if os.path.exists(token_pickle):
        with open(token_pickle, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_pickle, 'wb') as token:
            pickle.dump(creds, token)
    return creds


# ========================== EMAIL HANDLERS ============================= #
def connect_to_mailbox():
    try:
        creds = get_oauth2_token()
        auth_string = f'user={EMAIL_USER}\1auth=Bearer {creds.token}\1\1'
        mail = imaplib.IMAP4_SSL(EMAIL_IMAP)
        mail.authenticate('XOAUTH2', lambda x: auth_string.encode())
        return mail
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        return None



def decode_body(body_bytes):
    try:
        return body_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return body_bytes.decode('ISO-8859-1')
        except UnicodeDecodeError:
            return body_bytes.decode('utf-8', errors='replace')


def clean_body(body):
    return body.replace('\r\n', '\n').replace('\n\n', '\n')


def get_thread_id_from_msg_id(service, message_id):
    try:
        query = f"rfc822msgid:{message_id}"
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get("messages", [])
        if messages:
            msg_id = messages[0]["id"]
            full_msg = service.users().messages().get(userId='me', id=msg_id).execute()
            thread_id = full_msg.get("threadId")
            return thread_id
        else:
            print("❌ No email found with that Message-ID.")
            return None
    except Exception as e:
        print(f"Error fetching thread ID: {e}")
        return None

def get_message_subject(service, message_id):
    try:
        query = f"rfc822msgid:{message_id}"
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get("messages", [])
        if messages:
            msg_id = messages[0]["id"]
            full_msg = service.users().messages().get(userId='me', id=msg_id).execute()
            
            # Extract subject from headers
            headers = full_msg.get("payload", {}).get("headers", [])
            for header in headers:
                if header["name"].lower() == "subject":
                    return header["value"]
        
        return None
    except Exception as e:
        print(f"Error fetching message subject: {e}")
        return None
    
def get_rfc822_message_id(service, internal_id):
    """
    Fetches the RFC 822 'Message-ID' from Gmail internal message ID.
    """
    try:
        message = service.users().messages().get(
            userId='me',
            id=internal_id,
            format='metadata',
            metadataHeaders=['Message-ID']
        ).execute()

        headers = message.get('payload', {}).get('headers', [])
        rfc822_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), None)

        return rfc822_id
    except Exception as e:
        print(f"❌ Error fetching RFC 822 Message-ID: {e}")
        return None

def extract_thread_id(parsed_email):
    """
    Extract or generate a thread ID from email headers.
    Uses References and In-Reply-To headers to identify thread.
    """
    # Check if we have References header with multiple IDs (indicating a thread)
    if parsed_email.get("references"):
        refs = parsed_email.get("references").strip().split()
        if refs:
            # Use the first reference as thread ID (original message)
            return refs[0]
    
    # Check if we have In-Reply-To header
    if parsed_email.get("in_reply_to"):
        return parsed_email.get("in_reply_to")
    
    # If no thread indicators, use the message's own ID as thread ID
    return parsed_email.get("message_id")
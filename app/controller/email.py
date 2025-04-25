import os
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
import app.utils.mongo_utils as mongo
from app.Helper import email_helper

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_IMAP = os.getenv("EMAIL_IMAP")
SCOPES = ['https://mail.google.com/']


# ========================== MAIN FETCH FUNCTION ============================= #
def fetch_unread_emails(mail, keyword=None):
    emails = []
    det_emails = []
    result = []

    mail.select("inbox")
    email_helper.create_processed_folder(mail)

    status, messages = email_helper.search_emails(mail, keyword)
    if status != "OK":
        print("No messages found!")
        return {"email": [], "Response": None}

    for num in messages[0].split():
        status, msg_data = mail.fetch(num, '(RFC822)')
        if status != "OK":
            print(f"Failed to fetch email {num}")
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                parsed_email = email_helper.parse_email_from_bytes(response_part)
                # process_email_content(parsed_email["subject"], parsed_email["from"], parsed_email["body"], parsed_email["message_id"])
                # checkreply = email_helper.check_reply(response_part)
                emails.append({
                    "subject": parsed_email.get("subject"),
                    "from": parsed_email.get("from"),
                    "body": parsed_email.get("body")
                })
                det_emails.append({
                    "subject": parsed_email.get("subject"),
                    "from": parsed_email.get("from"),
                    "body": parsed_email.get("body"),
                    "message_id": parsed_email.get("message_id"),
                    "in_reply_to": parsed_email.get("in_reply_to"),
                    "references": parsed_email.get("references")
                })
        try:
            result = email_helper.handle_email_processing(emails)
            for email_body, response_data in zip(det_emails, result):
                mongo.save_data(email_body, response_data)  # Pass one email + one response
                email_helper.mark_as_processed(mail, num)
        except Exception as e:
            print(f"Error processing email {num}: {e}")
            email_helper.mark_unread(mail, num)

    mail.expunge()
    print("\nFetched Emails:", emails)
    return {"email": emails, "Response": result}

def get_all_email():
    return mongo.fetch_all_mails()

def get_all_tickets():
    return mongo.fetch_all_tickets()

def get_ticket_by_ticket_id(ticket_id):
    return mongo.fetch_ticket_by_ticket_id(ticket_id)
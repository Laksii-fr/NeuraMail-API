import app.utils.mongo_utils as mongo
from app.Helper import email_helper
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
import app.models.model_types as modelType

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_IMAP = os.getenv("EMAIL_IMAP")
SCOPES = ['https://mail.google.com/']

def send_email_via_oauth2(reply: modelType.EmailReply):
    try:
        creds = email_helper.get_oauth2_token()
        service = build('gmail', 'v1', credentials=creds)

        # Get thread ID and original message details
        thread_id = email_helper.get_thread_id_from_msg_id(service, reply.message_id)
        print(f"Thread ID: {thread_id}")
        
        # Get original message subject if available
        original_subject = email_helper.get_message_subject(service, reply.message_id)
        reply_subject = f"Re: {original_subject}" if original_subject else "Re: Your email"

        # Create the reply message
        mime_message = email_helper.MIMEMultipart()
        mime_message['From'] = EMAIL_USER
        mime_message['To'] = reply.to_email
        mime_message['Subject'] = reply_subject
        mime_message.attach(email_helper.MIMEText(reply.body, 'plain'))

        # Set proper reply headers
        if reply.message_id:
            mime_message.add_header('In-Reply-To', reply.message_id)
            mime_message.add_header('References', reply.message_id)

        raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        
        # Construct the message
        message = {'raw': raw_message}
        if thread_id:
            message['threadId'] = thread_id

        sent = service.users().messages().send(userId='me', body=message).execute()
        mongo.update_reply(reply)
        print(f"✅ Reply sent! Gmail Msg ID: {sent['id']}")
        return sent['id']
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        raise ValueError(f"Error sending email: {e}")

def get_full_thread(ticket_id):
    try:
        thread = mongo.get_full_thread(ticket_id)
        return thread
    except Exception as e:
        print(f"Error fetching thread: {e}")

def get_latest_email_message_by_ticket_id(ticket_id):
    try:
        latest_thread = mongo.get_latest_email_message_by_ticket_id(ticket_id)
        return latest_thread
    except Exception as e:
        print(f"Error fetching latest email threads: {e}")
        raise ValueError(f"Error fetching latest email threads: {e}")
    
def update_ticket_status(ticket_id, status):
    try:
        response = mongo.update_ticket_status(ticket_id, status)
        return response
    except Exception as e:
        print(f"Error updating ticket status: {e}")
        raise ValueError(f"Error updating ticket status: {e}")
# def create_ticket(subject, sender, body):
#     return f"TICKET-{int(time.time())}"


# def process_email_content(subject, sender, body, message_id):
#     try:
#         print(f"Processing Email Content: Subject: {subject}, From: {sender}")
#         ticket_id = create_ticket(subject, sender, body)

#         reply_subject = f"Re: {subject}"
#         reply_body = (
#             f"Dear {sender},\n\n"
#             f"Thank you for reaching out. Your ticket with ID {ticket_id} has been created successfully.\n"
#             f"Our team will get back to you shortly.\n\n"
#             f"Best regards,\nSupport Team"
#         )

#         send_email_via_oauth2(sender, reply_subject, reply_body, message_id)
#         print(f"Reply email sent to {sender}")

#     except Exception as e:
#         print(f"Error processing email from {sender}: {e}")

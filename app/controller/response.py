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
    """
    Send an email reply using OAuth2 authentication and properly maintain threading
    with RFC 822 Message-IDs.
    """
    try:
        # Get OAuth2 credentials and build Gmail service
        creds = email_helper.get_oauth2_token()
        service = build('gmail', 'v1', credentials=creds)
        
        # First, get the original email's RFC 822 Message-ID
        original_rfc822_id = get_original_rfc822_message_id(service, reply.message_id)
        if not original_rfc822_id:
            print(f"⚠️ Warning: Could not find original RFC 822 Message-ID for {reply.message_id}")
            
        # Get the original subject
        original_subject = get_original_subject(service, reply.message_id)
        reply_subject = f"Re: {original_subject}" if original_subject else "Re: Your email"
        
        # Create the MIME message
        mime_message = email_helper.MIMEMultipart()
        mime_message['From'] = EMAIL_USER
        mime_message['To'] = reply.to_email
        mime_message['Subject'] = reply_subject
        mime_message.attach(email_helper.MIMEText(reply.body, 'plain'))
        
        # Add proper threading headers using the original RFC 822 Message-ID
        if original_rfc822_id:
            mime_message.add_header('In-Reply-To', original_rfc822_id)
            mime_message.add_header('References', original_rfc822_id)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        
        # Prepare the message with threadId if available
        message = {'raw': raw_message}
        
        # Get the thread ID directly from the Gmail API based on the original message
        thread_id = get_thread_id(service, reply.message_id)
        if thread_id:
            message['threadId'] = thread_id
            print(f"📌 Using thread ID: {thread_id}")
        
        # Send the message
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        internal_id = sent_message['id']
        print(f"📤 Message sent with internal ID: {internal_id}")
        
        # Get the RFC 822 Message-ID of the sent message
        sent_rfc822_id = get_sent_rfc822_message_id(service, internal_id)
        
        # Update the reply in database with the new RFC 822 Message-ID
        mongo.update_reply(reply, sent_rfc822_id)
        
        print(f"✅ Reply sent successfully! RFC 822 Message-ID: {sent_rfc822_id}")
        return sent_rfc822_id
        
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)

def get_original_rfc822_message_id(service, message_id):
    """
    Get the RFC 822 Message-ID of the original email.
    Works whether message_id is an internal Gmail ID or an RFC 822 ID.
    """
    try:
        # If it looks like an RFC 822 ID already, just return it
        if message_id and message_id.startswith('<') and message_id.endswith('>'):
            return message_id
            
        # Check if it's a partial or complete RFC 822 ID without brackets
        if '@' in message_id:
            # Try to find the message using rfc822msgid query
            query = f"rfc822msgid:{message_id}"
        else:
            # It's probably an internal Gmail ID, try to get message directly
            try:
                msg = service.users().messages().get(
                    userId='me', 
                    id=message_id,
                    format='metadata',
                    metadataHeaders=['Message-ID']
                ).execute()
                
                headers = msg.get('payload', {}).get('headers', [])
                for header in headers:
                    if header['name'].lower() == 'message-id':
                        return header['value']
                return None
            except Exception:
                # If that fails, try using it as a search query
                query = f"rfc822msgid:{message_id}"
        
        # Search for the message
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print(f"❌ No message found with identifier: {message_id}")
            return None
            
        # Get the full message to extract headers
        internal_id = messages[0]['id']
        msg = service.users().messages().get(
            userId='me', 
            id=internal_id,
            format='metadata',
            metadataHeaders=['Message-ID']
        ).execute()
        
        # Extract the Message-ID header
        headers = msg.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == 'message-id':
                return header['value']
                
        return None
    except Exception as e:
        print(f"❌ Error getting original RFC 822 Message-ID: {str(e)}")
        return None

def get_original_subject(service, message_id):
    """
    Get the subject of the original email.
    """
    try:
        # Determine if message_id is an RFC 822 ID or internal ID
        if '@' in message_id:
            # It's likely an RFC 822 ID (or part of one)
            query = f"rfc822msgid:{message_id.strip('<>')}"
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            if not messages:
                print(f"❌ No message found with RFC 822 ID: {message_id}")
                return None
                
            internal_id = messages[0]['id']
        else:
            # Try using it as an internal ID
            internal_id = message_id
        
        # Get the message metadata with Subject header
        msg = service.users().messages().get(
            userId='me', 
            id=internal_id,
            format='metadata',
            metadataHeaders=['Subject']
        ).execute()
        
        # Extract the Subject header
        headers = msg.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == 'subject':
                # Remove any "Re:" prefix to avoid stacking
                subject = header['value']
                if subject.lower().startswith('re:'):
                    subject = subject[3:].strip()
                return subject
                
        return None
    except Exception as e:
        print(f"❌ Error getting original subject: {str(e)}")
        return None

def get_thread_id(service, message_id):
    """
    Get thread ID from a message identifier (internal ID or RFC 822 ID).
    """
    try:
        # Check if it's an RFC 822 ID (or part of one)
        if '@' in message_id:
            query = f"rfc822msgid:{message_id.strip('<>')}"
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            if not messages:
                print(f"❌ No message found with identifier: {message_id}")
                return None
                
            internal_id = messages[0]['id']
        else:
            # Try using it directly as an internal ID
            internal_id = message_id
        
        # Get the thread ID
        msg = service.users().messages().get(userId='me', id=internal_id, format='minimal').execute()
        thread_id = msg.get('threadId')
        
        return thread_id
    except Exception as e:
        print(f"❌ Error getting thread ID: {str(e)}")
        return None

def get_sent_rfc822_message_id(service, internal_id):
    """
    Get the RFC 822 Message-ID of a sent email using its internal Gmail ID.
    Retries up to 3 times with a small delay to ensure the message is fully processed.
    """
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            msg = service.users().messages().get(
                userId='me', 
                id=internal_id,
                format='metadata',
                metadataHeaders=['Message-ID']
            ).execute()
            
            headers = msg.get('payload', {}).get('headers', [])
            for header in headers:
                if header['name'].lower() == 'message-id':
                    return header['value']
            
            # If we didn't find it and haven't exhausted retries, wait and try again
            if attempt < max_retries - 1:
                print(f"⏳ Message-ID not found yet, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Error on attempt {attempt+1}: {str(e)}. Retrying...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"❌ Failed to get RFC 822 Message-ID after {max_retries} attempts: {str(e)}")
                return None
    
    print("❌ Could not retrieve RFC 822 Message-ID")
    return None



# def send_email_via_oauth2(reply: modelType.EmailReply):
#     try:
#         creds = email_helper.get_oauth2_token()
#         service = build('gmail', 'v1', credentials=creds)

#         # Get thread ID and original message details
#         thread_id = email_helper.get_thread_id_from_msg_id(service, reply.message_id)
#         print(f"Thread ID: {thread_id}")
        
#         # Get original message subject if available
#         original_subject = email_helper.get_message_subject(service, reply.message_id)
#         reply_subject = f"Re: {original_subject}" if original_subject else "Re: Your email"

#         # Create the reply message
#         mime_message = email_helper.MIMEMultipart()
#         mime_message['From'] = EMAIL_USER
#         mime_message['To'] = reply.to_email
#         mime_message['Subject'] = reply_subject
#         mime_message.attach(email_helper.MIMEText(reply.body, 'plain'))

#         # Set proper reply headers
#         if reply.message_id:
#             mime_message.add_header('In-Reply-To', reply.message_id)
#             mime_message.add_header('References', reply.message_id)

#         raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        
#         # Construct the message
#         message = {'raw': raw_message}
#         if thread_id:
#             message['threadId'] = thread_id

#         sent = service.users().messages().send(userId='me', body=message).execute()
#         mongo.update_reply(reply)
#         print(f"✅ Reply sent! Gmail Msg ID: {sent['id']}")
#         return sent['id']
#     except Exception as e:
#         print(f"❌ Error sending email: {e}")
#         raise ValueError(f"Error sending email: {e}")

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

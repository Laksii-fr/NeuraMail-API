from app.utils.mongo_utils import get_pending_replies
from app.models.model_types import EmailReply
from app.controller.response import send_email_via_oauth2
import app.Helper.api_caller as api_caller
import app.utils.mongo_utils as mongo

def auto_reply_to_pending_emails(user_id: str):
    print(f"🔍 Fetching pending replies for user_id: {user_id}")
    pending = get_pending_replies(user_id)
    print(f"📋 Found {len(pending)} pending replies for user_id: {user_id}")
    
    for doc in pending:
        print(f"✉️ Processing ticket_no: {doc['ticket_no']}")
        body = automate_reply(doc["ticket_no"], user_id)
        print("Body :", body)
        latest_message_id = doc["Thread"][-1].get("message_id")
        reply = EmailReply(
            ticket_id=str(doc["ticket_no"]),
            to_email=doc["sender_email"],
            body=body,
            message_id=latest_message_id
        )
        print("Proceeding to send email")
        try:
            print("Body going forward :", reply)
            print(f"📤 Sending email for ticket_no: {reply.ticket_id}")
            send_email_via_oauth2(reply)
            print(f"✅ Successfully sent email for ticket_no: {reply.ticket_id}")
        except Exception as e:
            print(f"❌ Failed to send reply for ticket {reply.ticket_id}: {e}")
            raise ValueError(f"❌ Failed to send reply for ticket {reply.ticket_id}: {e}")
        

def automate_reply(ticket_id, user_id) -> str:
    print(f"🔄 Automating reply for ticket_id: {ticket_id}, user_id: {user_id}")
    context = mongo.get_thread_context_by_ticket_no(ticket_id, user_id)
    print(f"📜 Retrieved thread context for ticket_id: {ticket_id} Context : {context}")
    messages = str(context)
    print(f"📨 Sending context to API for ticket_id: {ticket_id}")
    response = api_caller.send_message_to_api(user_id, messages)
    print(f"📬 Received response from API for ticket_id: {ticket_id}")
    message = str(response)
    return message
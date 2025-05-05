from fastapi import APIRouter, Depends
import app.models.model_types as modelType
import app.controller.cognito as auth
import app.controller.response as email
router = APIRouter()

@router.post("/reply-to-email")
def reply_to_email(reply: modelType.EmailReply,
                   user: dict = Depends(auth.get_current_user)):
    try:
        user_id = user.get('login_id')
        email.send_email_via_oauth2(reply)
        return {
            "status": "success",
            "message": "Email sent successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error sending email: {e}"
        }
    
@router.get("/get-full-thread")
def get_all_threads(ticket_id: str,
                    user: dict = Depends(auth.get_current_user)):
    try:
        user_id = user.get('login_id')
        response = email.get_full_thread(ticket_id)
        return {
            "status": "success",
            "message": "Thread fetched successfully",
            "data": response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching thread: {e}"
        }
    
@router.get("/get-latest-email-threads")
def get_latest_email_threads_by_ticket_id(ticket_id: str,
                                          user: dict = Depends(auth.get_current_user)):
    try:
        user_id = user.get('login_id')
        response = email.get_latest_email_message_by_ticket_id(ticket_id)
        return {
            "status": "success",
            "message": "Latest email threads fetched successfully",
            "data": response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching latest email threads: {e}"
        }
    
@router.post("/update_ticket_status")
def update_ticket_status(ticket_id: str, status: str,
                         user: dict = Depends(auth.get_current_user)):
    try:
        user_id = user.get('login_id')
        response = email.update_ticket_status(ticket_id, status)
        return {
            "status": "success",
            "message": "Ticket status updated successfully",
            "data": response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating ticket status: {e}"
        }
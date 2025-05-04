from fastapi import APIRouter, Depends
import app.models.model_types as modelType
import app.controller.automated_response as response
from app.controller.cognito import get_current_user

router = APIRouter()

@router.post("/automated-response/reply-to-email")
def reply_to_email(user : dict = Depends(get_current_user)):
    try:
        user_id = user.get('login_id')
        response.auto_reply_to_pending_emails(user_id)
        return {
            "status": "success",
            "message": "Email sent successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error sending email: {e}"
        }
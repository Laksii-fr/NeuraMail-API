from fastapi import APIRouter
import app.controller.email as email
import app.Helper.email_helper as Ehelper
router = APIRouter()

@router.get("/emails")
def read_emails(keyword: str = None):
    mail = Ehelper.connect_to_mailbox()
    if mail:
        emails = email.fetch_unread_emails(mail, keyword)
        mail.logout()
        return {"emails": emails}
    else:
        return {"error": "Failed to connect to the mailbox."}

@router.get('/get-all-queries')
def get_all_queries():
    try : 
        response = email.get_all_email()
        return {
            "status": "success",
            "message": "Queries Fetched Successfully",
            "data": response
        }
    except Exception as e : 
        return f"Error {e}"

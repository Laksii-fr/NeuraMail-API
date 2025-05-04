from fastapi import APIRouter, Depends
import app.controller.email as email
import app.Helper.email_helper as Ehelper
from app.controller.cognito import get_current_user
router = APIRouter()

@router.get("/emails")
def read_emails(keyword: str = None,
                user: dict = Depends(get_current_user)):
    try : 
        user_id = user.get('login_id')
        mail = Ehelper.connect_to_mailbox()
        if mail:
            emails = email.fetch_unread_emails(mail, keyword, user_id)
            mail.logout()
            return {"emails": emails}
        else:
            return {"error": "Failed to connect to the mailbox."}
    except Exception as e : 
        return f"Error {e}"
    
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
    
@router.get('/get-all-tickets')
def get_all_tickets():
    try : 
        response = email.get_all_tickets()
        return {
            "status": "success",
            "message": "Tickets Fetched Successfully",
            "data": response
        }
    except Exception as e : 
        return f"Error {e}"

# @router.get("/get-ticket-by-ticket-id")
# def get_ticket_by_ticket_id(ticket_id: str):
#     try : 
#         response = email.get_ticket_by_ticket_id(ticket_id)
#         return {
#             "status": "success",
#             "message": "Ticket Fetched Successfully",
#             "data": response
#         }
#     except Exception as e : 
#         return f"Error {e}"
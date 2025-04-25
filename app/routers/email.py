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
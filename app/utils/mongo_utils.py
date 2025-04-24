from app.database import SavedQueries
from datetime import datetime
import app.models.model_types as modeltype
import uuid



def fetch_all_mails():
    try:
        cur = SavedQueries.find(
            # filter=filter_conditions, 
            projection={
                "_id": 0,
            }
        ).sort([("createdAt", -1)])

        # Convert cursor to list
        result = [doc for doc in cur]

        return result
    
    except Exception as e:
        print(f"Error: {e}")
        return f"Something went wrong during fetching Emails.{e}"
        
from app.database import UsersCollection
from fastapi import HTTPException, status
from datetime import datetime, timedelta

def find_user_by_email(email: str):
    """Find a user by email."""
    return UsersCollection.find_one({"email": email})

def insert_new_user(email: str, sub_id: str, is_confirmed: bool = False):
    """Insert a new user into the database."""
    print("A.3.1 Proceeding to Save data")
    credits = 20 #Credits to new Account
    print("A.3.1 Proceeding to Save data with credtis" , credits)
    user_data = {
        "email": email,
        "sub_id": sub_id,
        "Remaining_Creds" : credits,
        "is_confirmed": is_confirmed
    }
    
    print("data being saved",user_data)

    return UsersCollection.insert_one(user_data)

def update_user_confirmation_status(email: str, is_confirmed: bool):
    """Update the confirmation status of a user."""
    return UsersCollection.update_one(
        {"email": email},
        {"$set": {"is_confirmed": is_confirmed}}
    )

def save_user_info(email: str, sub_id: str = None, is_confirmed: bool = False):
    try:
        # Define the update operation
        update_operation = {
            "email": email,
            "is_confirmed": is_confirmed
        }

        # Only update sub_id if it is provided
        if sub_id:
            update_operation["sub_id"] = sub_id

        # Use upsert=True to create the document if it doesn't exist
        UsersCollection.update_one(
            {"email": email},
            {"$set": update_operation},
            upsert=True
        )

    except Exception as e:
        print(f"Error saving user info: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while saving user info: {str(e)}")
    
async def decrement_remaining_credits(sub_id, credits):
    """
    Decrement the Remaining_Creds by 1 for a user in UsersCollection.

    Args:
        sub_id (str): The subscription ID of the user.

    Returns:
        dict: The updated user document if successful, or raises an exception if the user does not exist or has insufficient credits.
    """
    try:
        print(f"Decrementing 1 credit for sub_id: {sub_id}")

        # Query to match the user with sufficient Remaining_Creds
        filter_query = {"sub_id": sub_id, "Remaining_Creds": {"$gt": 0}}

        # Update operation to decrement Remaining_Creds
        update_query = {
            "$inc": {"Remaining_Creds": -credits}, 
            "$set": {"updatedAt": datetime.utcnow().isoformat()}  # Update the timestamp
        }

        # Find and update the document
        result = UsersCollection.find_one_and_update(
            filter_query,
            update_query,
            return_document=True  # Return the updated document
        )

        # Handle case where user is not found or credits are insufficient
        if not result:
            raise HTTPException(
                status_code=400,
                detail=f"User with sub_id {sub_id} not found or has insufficient credits."
            )

        print(f"Remaining_Creds decremented successfully for sub_id: {sub_id}")
        return result

    except Exception as e:
        print(f"Error decrementing Remaining_Creds: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to decrement Remaining_Creds in UsersCollection. {e}",
        )
    
def get_remaining_credits(sub_id):
    print("Fetching remaining tokens for sub_id:", sub_id)
    user = UsersCollection.find_one({"sub_id": sub_id}, {"Remaining_Creds": 1})
    
    if user:
        remaining_tokens = user.get("Remaining_Creds", 0)
        print("Remaining tokens found:", remaining_tokens)
        return remaining_tokens
    else:
        print("User not found for sub_id:", sub_id)
        return None


def save_data(body, data):
    print({"Body": body})
    print({"data": data})
    try:
        ticket_no = data['ticket_no'] or data['ticket_id']

        # Fallback: Try identifying thread via message reply
        if not ticket_no or ticket_no == "None":
            in_reply_to = body["in_reply_to"] or body["references"]
            if in_reply_to:
                thread = SavedQueries.find_one({
                    "Thread.message_id": in_reply_to
                })
                if thread:
                    ticket_no = thread["ticket_no"]

        # Final fallback: generate a new ticket ID
        if not ticket_no or ticket_no == "None":
            ticket_no = uuid.uuid4().hex[:16].upper()
            new_query = {
                "ticket_no": ticket_no,
                "sender_email": body["from"],
                "Subject": body["subject"],
                "request_type": data["request_type"],
                "Thread": [
                    {
                        "message_id": body["message_id"],
                        "request_description": data["request_description"],
                        "email_body": body["body"],
                        "Reply": None,
                        "timestamp": datetime.utcnow()
                    }
                ],
                "status": "open",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }
            SavedQueries.insert_one(new_query)
        else:
            # Append to existing ticket
            SavedQueries.update_one(
                {"ticket_no": ticket_no},
                {
                    "$push": {
                        "Thread": {
                            "message_id": body["message_id"],
                            "request_description": data["request_description"],
                            "email_body": body["body"],
                            "timestamp": datetime.utcnow()
                        }
                    },
                    "$set": {
                        "updatedAt": datetime.utcnow()
                    }
                }
            )

        return f"Saved data under ticket {ticket_no}"

    except Exception as e:
        print(f"Error: {e}")
        raise ValueError(f"Error saving Queries in Database: {e}")
    
def get_full_thread(ticket_id):
    try:
        thread_data = SavedQueries.find_one({"ticket_no": ticket_id})
        if not thread_data:
            raise HTTPException(status_code=404, detail="Thread not found")

        thread_summary = []
        sender_email = thread_data.get("sender_email")
        for item in thread_data.get("Thread", []):
            summary = {
                "message_id": item.get("message_id"),
                "request_type": thread_data.get("request_type"),
                "request_description": item.get("request_description")
            }
            print("Summary:", summary)
            thread_summary.append(summary)
        return {
            "ticket_no": ticket_id,
            "sender_email": sender_email,
            "thread_summary": thread_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching thread summary: {str(e)}")


def update_reply(reply : modeltype.EmailReply):
    try:
        # Update the thread with the reply
        SavedQueries.update_one(
            {"ticket_no": reply.ticket_id},
            {
                "$set": {
                    "Thread.$[elem].Reply": reply.body,
                    "Thread.$[elem].timestamp": datetime.utcnow()
                }
            },
            array_filters=[{"elem.message_id": reply.message_id}]
        )
        return {"status": "success", "message": "Reply updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating reply: {str(e)}")
    
def get_latest_email_message_by_ticket_id(ticket_id: str):
    try:
        # Fetch the document by ticket_no
        ticket_data = SavedQueries.find_one({"ticket_no": ticket_id})
        sender_email = ticket_data.get("sender_email") if ticket_data else None
        request_type = ticket_data.get("request_type") if ticket_data else None
        if not ticket_data or "Thread" not in ticket_data or not ticket_data["Thread"]:
            raise HTTPException(status_code=404, detail="No threads found for this ticket ID")

        # Sort the Thread array by timestamp in descending order and return the first
        latest_message = sorted(ticket_data["Thread"], key=lambda x: x["timestamp"], reverse=True)[0]
        return {
            "sender_email" : sender_email, 
            "request_type" : request_type, 
            "ticket_no" : ticket_id,
            "Latest Message" : latest_message
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching the latest email message: {str(e)}")

def update_ticket_status(ticket_id: str, status: str):
    try:
        # Update the ticket status
        result = SavedQueries.update_one(
            {"ticket_no": ticket_id},
            {"$set": {"status": status}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Ticket not found or status unchanged")
        return {"status": "success", "message": "Ticket status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ticket status: {str(e)}")
from app.database import SavedQueries

# Ensure the database connection is properly initialized


def get_thread_context_by_ticket_no(ticket_no: str, userid: str):
    ticket = SavedQueries.find_one({"ticket_no": ticket_no, "user_id": userid})
    if ticket is None:
        print("Debug: No ticket found for the given query.")
        raise ValueError("Database connection is not properly configured. 'tickets' collection is missing.")

    if not ticket:
        return {"error": "Ticket not found"}

    thread_context = {
        "request_type": ticket.get("request_type"),
        "thread": []
    }

    for entry in ticket.get("Thread", []):
        # Customer's message
        if "email_body" in entry and entry["email_body"]:
            thread_context["thread"].append({
                "from": "Customer",
                "body": entry["email_body"]
            })
        # Support's reply
        if "Reply" in entry and entry["Reply"]:
            thread_context["thread"].append({
                "from": "Support",
                "body": entry["Reply"]
            })

    return thread_context


print(get_thread_context_by_ticket_no("7B143EE49BBE4388", "71f32dba-3061-70ce-bafc-91ba2e7a5f3b"))
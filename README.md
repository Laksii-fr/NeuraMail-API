
# NeuraMail

A smart, scalable, and fully-automated email processing assistant built using **FastAPI**, **MongoDB**, and **Gmail API (OAuth2)**.

## 🚀 Features

- **Automated Ticketing System**  
  Converts incoming emails into support tickets with unique ticket IDs.

- **Threaded Conversations**  
  Emails are threaded and stored based on message context using `Message-ID`, `In-Reply-To`, and `References` headers.

- **Smart Reply Extraction**  
  Extracts only the new reply content using the `email-reply-parser`, discarding quoted messages.

- **Database Integration**  
  Stores complete email threads and updates existing tickets in MongoDB.

- **Gmail Integration with OAuth2**  
  Sends replies via Gmail while maintaining message threading with correct headers.

## 🛠 Tech Stack

- **Backend**: FastAPI  
- **Database**: MongoDB  
- **Email API**: Gmail (OAuth2)  
- **Parsing**: `email-reply-parser`, `email`, `imaplib`, `smtplib`  
- **Other**: PyMongo, Uvicorn, Python's built-in `uuid`, `datetime`, etc.

## 📁 Project Structure

```
/app
  ├── controller/
  ├── helper/
  ├── router/
  ├── models/
  ├── utils/
  └── main.py
```

## 📄 Endpoints

- `POST /email/send`: Send a reply email
- `GET /email/unread`: Fetch unread emails
- `GET /email/thread/{ticket_id}`: Fetch full thread by ticket ID

## 🔐 Authentication

All email operations use OAuth2 authentication with Google's Gmail API. Make sure to set up your credentials properly in the `token.json` or environment.

## 🧪 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI app
uvicorn app.main:app --reload
```

## 📬 Sample Email Flow

1. Customer sends an email ➝ Parsed and stored with `ticket_no`
2. Staff replies ➝ Email sent via Gmail with correct headers
3. Future replies by customer ➝ Appends to the same ticket thread

## ✅ TODO

- Add admin dashboard
- Include email categorization (e.g., Refunds, Complaints)
- Add email notification system

---

### ⚠️ Disclaimer

This project is not affiliated with Google. Use responsibly and respect email usage policies.

---

### 😂 Final Note

If this bot ever emails your boss “yes” instead of “yes, absolutely, I’ll get on it right away”, blame the AI—not you. 😉

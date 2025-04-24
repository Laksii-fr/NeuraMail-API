
# 📬 Email Assistant AI 🤖📥

Welcome to **Email Assistant**, your personal AI-powered Gmail butler that reads, replies, and organizes your inbox like a caffeinated octopus with 8 keyboards! 🐙💻💻💻💻💻💻💻💻

## ✨ What it does

🚀 **Reads unread emails**  
🕵️‍♂️ **Extracts only the *latest reply*** (no long quote-trains, promise)  
📎 **Maintains threads like a Gmail ninja**  
🧠 **Understands who said what using EmailReplyParser magic**  
📨 **Sends replies via Gmail API with threading like a pro**  
🧾 **Stores ticketed threads in MongoDB** (because we’re professionals, duh)  

---

## 🧠 Tech Stack

| Tech | Purpose |
|------|---------|
| Python 🐍 | Backend wizardry |
| FastAPI ⚡ | Lightning-fast APIs |
| Gmail API 📬 | To rule the inbox |
| OAuth2 🔐 | Auth that’s safe & smooth |
| MongoDB 🍃 | Store tickets & threads |
| EmailReplyParser 🧵 | Splits quoted text from actual replies |
| Google Apps Script 🤖 (optional) | For testing on the Google side |

---

## ⚙️ Setup Instructions

1. Clone the madness:
   ```bash
   git clone https://github.com/you/email-assistant.git
   cd email-assistant
   ```

2. Create your virtual cave:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the potions:
   ```bash
   pip install -r requirements.txt
   ```

4. Setup your `.env` with:
   ```
   EMAIL_USER=your_email@gmail.com
   CLIENT_ID=...
   CLIENT_SECRET=...
   REFRESH_TOKEN=...
   ```

5. Fire it up:
   ```bash
   uvicorn main:app --reload
   ```

---

## 🔥 Cool Features

### 📩 Fetch Unread Emails
```bash
GET /emails/unread
```
Returns the freshest replies from users—no more reading the entire conversation thread from the beginning of time.

### 🧵 Get Full Thread by Ticket
```bash
GET /emails/thread/{ticket_id}
```
Get the entire chain of sorrow and hope tied to a ticket.

### 📨 Reply Like a Boss
```bash
POST /emails/reply
```
Send a reply that lands **inside** the thread—not as a new message! (We know what threading is. We respect it.)

### 🕵️ Retrieve by Message ID
```bash
GET /emails/message/{message_id}
```
Want to inspect if you’re replying to the right message? Sherlock Holmes mode activated.

---

## 😎 Sample Payloads

**Reply Example:**
```json
{
  "to_email": "client@example.com",
  "body": "We’ve processed your refund.",
  "message_id": "<CAEG-Ar1oQSAMFH8SPAuvy@mail.gmail.com>"
}
```

---

## 🧨 Future Ideas

- ✅ Smart auto-replies powered by GPT
- 📅 Auto-schedule meetings from threads
- 🗂️ Automatic tagging based on request type
- 🧵 Conversation sentiment heatmaps (yeah, wild!)

---

## 🧙‍♂️ Contributors

- **You** – the sorcerer of inbox automation  
- **GPT + FastAPI** – the spellbook  
- **MongoDB** – the vault of ticket wisdom  

---

## 🫶 Made with love, caffeine & `In-Reply-To` headers.

Give this repo a ⭐ if your inbox needs a hero.

import requests
import os
import app.Helper.openai_helper as ai_helper
import app.models.model_types as model_type
import app.utils.mongo_utils as mongo
import asyncio

def extract_content_from_json(email_json):
    """
    Extracts the subject, sender, and body from the provided email JSON.

    :param email_json: A list of dictionaries containing email details like subject, sender, and body.
    :return: A list of dictionaries containing extracted subject, sender, and body.
    """
    extracted_emails = []

    # Loop through the list of emails
    for email in email_json:  # Since email_json is a list, no need to use .get()
        subject = email.get('subject', '')
        sender = email.get('from', '')
        body = email.get('body', '')

        # Clean up the body if necessary (for consistency)
        body_clean = body.replace('\\n', '\n')

        # Add the extracted details to the list
        extracted_emails.append({
            'subject': subject,
            'sender': sender,
            'body': body_clean
        })

    return extracted_emails

def create_chat(body, user_id):
    thread = ai_helper.create_thread()

    # Formatting message content to be a single dictionary
    formatted_message = f'{{"text": {{"value":"Sender: {body["Sender"]}\\nSubject: {body["Subject"]}\\nEmail: {body["Email"]}"}}}}'

    astId = mongo.get_assistant_id(user_id)

    chat_instance = model_type.AssistantChat(
        astId=astId,
        threadId=thread.id,
        message=formatted_message  # Pass formatted message as a single dictionary
    )

    # Await the response since create_new_chat is asynchronous
    response = asyncio.run(ai_helper.create_new_chat([chat_instance]))

    return response



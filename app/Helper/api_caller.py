import requests
import app.utils.mongo_utils as mongo
import os

url = os.getenv("API_URL")

def send_message_to_api(userId , message) -> dict:
    assistant_token = mongo.get_assistant_token(userId)

    data = {
        "astName": "Untitled Assistant",
        "apiToken": assistant_token,
        "message": message
    }

    try:
        response = requests.post(url, data=data, headers={"accept": "application/json"})
        response.raise_for_status()
        json_response = response.json()
        assistant_message = json_response["data"][0][0]["message"]
        print("Assistant MEssage :",assistant_message)
        return assistant_message

    except (requests.RequestException, KeyError, IndexError) as e:
        raise ValueError(f"Error: {str(e)}")

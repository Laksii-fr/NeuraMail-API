import app.utils.mongo_utils as mongo
import app.models.model_types as modeltype
import app.Helper.openai_helper as openai_helper
import os
def get_profile(user_id: str):
    try:
        # Fetch the profile from the database
        profiles = mongo.get_profile(user_id)
        if not profiles:
            raise ValueError("Profile not found")
        
        # Return the first profile found
        return profiles
    
    except Exception as e:
        raise e
def create_profile(profile :modeltype.CreateProfile, user_id: str):
    try:
        # Create a new profile in the database
        new_profile = mongo.create_profile(profile, user_id)
        return new_profile
    
    except Exception as e:
        raise e

def update_profile(profile : modeltype.CreateProfile, user_id: str):
    try:
        # Fetch the profile from the database
        profiles = mongo.get_profile(user_id)
        if not profiles:
            raise ValueError("Profile not found")
        
        # Update the profile in the database
        updated_profile = mongo.update_profile(profile, user_id)
        return updated_profile
    
    except Exception as e:
        raise e

def update_req_types(types: list[str], user_id: str):
    # Load prompt template from file
    prompt_path = os.path.join("app", "Prompt", "prompt.txt")
    with open(prompt_path, "r") as f:
        prompt_template = f.read()

    # Format the request types
    formatted_types = "\n  - " + "\n  - ".join(types)
    final_prompt = prompt_template.replace("{request_types}", formatted_types)

    #create a assistant
    assistant = openai_helper.create_assistant(final_prompt)

    # save the assistant to the database
    mongo.update_profile_with_assistant_id(user_id, assistant.id)

    return {
        "prompt": final_prompt,
        "updated_types": types
    }

def update_assistant_token(token: str, user_id: str):
    try:
        # Update the assistant token in the database
        updated_profile = mongo.update_assistant_token(token, user_id)
        return updated_profile
    
    except Exception as e:
        raise e
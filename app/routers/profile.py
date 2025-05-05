from fastapi import APIRouter, HTTPException, Depends
import app.models.model_types as modelType
from app.controller.cognito import get_current_user
import app.controller.profile as pro

router = APIRouter()

@router.post("/create-profile")
def create_profile(profile: modelType.CreateProfile,
                   user: dict = Depends(get_current_user)):
    try:
        user_id = user.get('login_id')
        response = pro.create_profile(profile, user_id)
        return {
            "status": "success",
            "message": "Profile created successfully.",
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/update-profile")
def update_profile(profile : modelType.UpdateProfile, user: dict = Depends(get_current_user)):
    try:
        user_id = user.get('login_id')
        response = pro.update_profile(profile, user_id)
        return {
            "status": "success",
            "message": "Profile updated successfully.",
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-req-types")
def update_req_types(types: list[str],
                     user: dict = Depends(get_current_user)):
    try:
        user_id = user.get('login_id')
        response = pro.update_req_types(types, user_id)
        return {
            "status": "success",
            "message": "Profile updated successfully.",
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-assistant-token")
def update_assistant_token(token: str,
                            user: dict = Depends(get_current_user)):
    try:
        user_id = user.get('login_id')
        response = pro.update_assistant_token(token, user_id)
        return {
            "status": "success",
            "message": "Profile updated successfully.",
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/get-profile")
def get_profile(user: dict = Depends(get_current_user)):
    try:
        user_id = user.get('login_id')
        response = pro.get_profile(user_id)
        return {
            "status": "success",
            "message": "Profile fetched successfully.",
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
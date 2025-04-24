from fastapi import APIRouter, HTTPException, Depends
import app.controller.cognito as auth
import app.models.model_types as modelType
from fastapi.security import HTTPBearer

router = APIRouter()

oauth2_scheme = HTTPBearer()

@router.post("/sign-up")
async def sign_up(sign_up_request: modelType.SignUpRequest):
    try:
        print("A")
        response = await auth.sign_up_user(
            email=sign_up_request.email,
            password=sign_up_request.password,
        )
        return {
            "status": "success",
            "message": "User signed up successfully. Please check your email to confirm your account.",
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirm-sign-up")
async def confirm_sign_up(confirm_request: modelType.ConfirmUserRequest):
    try:
        auth.confirm_user(confirm_request.email, confirm_request.confirmation_code)
        return {"status": "success", "message": "User confirmed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    
@router.post("/resend-confirmation-code")
async def resend_confirmation_code_route(username: str):
    try:
        response = auth.resend_confirmation_code(username)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/password-reset/initiate")
async def initiate_password_reset_route(request: modelType.InitiatePasswordResetRequest):
    try:
        response = await auth.initiate_password_reset(email=request.email)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/password-reset/confirm")
async def confirm_password_reset_route(request: modelType.ConfirmPasswordResetRequest):
    try:
        response = await auth.confirm_password_reset(
            email=request.email,
            confirmation_code=request.confirmation_code,
            new_password=request.new_password
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/login")
async def login_user(login_request: modelType.LoginRequest):
    auth_result = auth.authenticate_user(login_request.email, login_request.password)
    login_id = auth.extract_sub_from_token(auth_result['AccessToken'])
    return {
        "status": True,
        "message": "Login successful",
        "access_token": auth_result['AccessToken'],
        "login_id": login_id 
    }

from fastapi import UploadFile
from datetime import datetime
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr, constr
from typing import *

class InitiatePasswordResetRequest(BaseModel):
    email: str

class ConfirmPasswordResetRequest(BaseModel):
    email: str
    confirmation_code: str
    new_password: constr(min_length=8)

class ConfirmUserRequest(BaseModel):
    email: str
    confirmation_code: str

class SignUpRequest(BaseModel):
    email: str
    password: constr(min_length=8)

class LoginRequest(BaseModel):
    email: str
    password: str

class AssistantChat(BaseModel):
    astId: str
    threadId: str
    message: str

class EmailReply(BaseModel):
    ticket_id: str
    to_email: str
    body: str
    message_id: str

class CreateProfile(BaseModel):
    name: str
    email: EmailStr
    phone: str

class UpdateProfile(BaseModel):
    name: str
    email: EmailStr
    phone: str
    auto_reply: bool
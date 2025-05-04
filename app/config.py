from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
        CLIENT_ORIGIN: str
        DATABASE_URL: str
        MONGO_INITDB_DATABASE: str
        EMAIL_USER : str
        EMAIL_IMAP : str
        OPENAI_API_KEY : str
        # Cognito settings
        API_URL: str
        COGNITO_USER_POOL_ID: str
        COGNITO_REGION: str
        COGNITO_CLIENT_ID: str
        COGNITO_CLIENT_SECRET: str


        class Config:
                env_file = './.env'

 
settings = Settings()

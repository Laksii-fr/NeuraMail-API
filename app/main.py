from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

load_dotenv()
from app.config import settings
from app.routers import email, auth, response
app = FastAPI()

origins = [settings.CLIENT_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Authentication"], prefix="/api/auth")
app.include_router(email.router, tags=["Email Processing"], prefix="/api/email")
app.include_router(response.router, tags=["Email Response"], prefix="/api/response")


@app.get("/health")
async def root():
    return {"message": "API is working fine."}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="127.0.0.1", port=8000, log_level="info", reload=True
    )

# App run command
# uvicorn app.main:app --reload

# Swagger URL for this API's
# http://127.0.0.1:8000/docs#/

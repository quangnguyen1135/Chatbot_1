from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from backend.chat_bot_backend import handle_userinput
from firebase_utils import save_chat_history
from typing import List, Dict, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin SDK only if it hasn't been initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase/chatbot-df502-firebase-adminsdk-56sbd-48189d1535.json')
    firebase_admin.initialize_app(cred)

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Create an instance of the FastAPI app
app = FastAPI(
    title="Chat Bot Cawana",
    description="Endpoints for the Cawana company chatbot",
)

db = firestore.client()

# Define the data model for user input
class UserInput(BaseModel):
    user_input: str
    session_id: Optional[str] = None  # Make session_id optional

class ChatHistory(BaseModel):
    messages: List[Dict[str, str]]

# In-memory storage for responses
responses = []

# Set up OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dummy token for demonstration
API_TOKEN = os.getenv("API_TOKEN")

# Define a function to verify the token
def verify_token(token: str = Depends(oauth2_scheme)):
    if token != API_TOKEN:
        # Return HTTP 401 Unauthorized if the token is invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        # Log the received token
        print(f"Received token: {token}")

# Define the root route for the API
@app.get("/")
async def home():
    return {"message": "Welcome to the Cawana chatbot API. Visit /docs for the API documentation."}

# Define the endpoint to handle user input and return a response
@app.post("/chat_bot_api", dependencies=[Depends(verify_token)])
async def get_response(user_input: UserInput):
    chat_history = []  # Initialize empty chat history for now
    response = handle_userinput(user_input.user_input, chat_history)
    # Store the response in memory
    responses.append({"user_input": user_input.user_input, "response": response})

    # Save chat history
    save_chat_history(user_input.user_input, response, user_input.session_id)
    
    return {"response": response}

# Define the endpoint to get all responses
@app.get("/chat_bot_responses", dependencies=[Depends(verify_token)])
async def get_all_responses():
    return {"responses": responses}

# Run the FastAPI app using Uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

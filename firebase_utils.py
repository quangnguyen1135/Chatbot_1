import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase Admin SDK only if it hasn't been initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase/chatbot-df502-firebase-adminsdk-56sbd-48189d1535.json')
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def save_chat_history(user_question, response, session_id):
    """Save chat history to Firebase Firestore."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().isoformat()
    
    chat_doc_ref = db.collection('chat_history').document(date_str)
    chat_data = chat_doc_ref.get()

    if chat_data.exists:
        chat_data_dict = chat_data.to_dict()
        sessions = chat_data_dict.get("sessions_id", {})
        if session_id in sessions:
            session_data = sessions[session_id]
            session_data["messages"].append({
                "role": "user", "content": user_question, "timestamp": timestamp
            })
            session_data["messages"].append({
                "role": "assistant", "content": response, "timestamp": timestamp
            })
            sessions[session_id] = session_data
        else:
            sessions[session_id] = {
                "session_id": session_id,
                "messages": [
                    {"role": "user", "content": user_question, "timestamp": timestamp},
                    {"role": "assistant", "content": response, "timestamp": timestamp}
                ]
            }
        chat_data_dict["sessions_id"] = sessions
        chat_doc_ref.set(chat_data_dict)
    else:
        chat_data_dict = {
            "sessions_id": {
                session_id: {
                    "session_id": session_id,
                    "messages": [
                        {"role": "user", "content": user_question, "timestamp": timestamp},
                        {"role": "assistant", "content": response, "timestamp": timestamp}
                    ]
                }
            }
        }
        print(f"Creating new document at chat_history/{date_str} with data: {chat_data_dict}")
        chat_doc_ref.set(chat_data_dict)


def fetch_chat_history(date_str, session_id):
    """Fetch chat history from Firebase Firestore."""
    print(f"Fetching chat history for date: {date_str} and session_id: {session_id}")
    chat_doc_ref = db.collection('chat_history').document(date_str).collection('sessions_id').document(session_id)
    chat_data = chat_doc_ref.get()
    if chat_data.exists:
        chat_data_dict = chat_data.to_dict()
        print(f"Chat data found: {chat_data_dict}")
        return chat_data_dict
    else:
        print(f"No chat history found for date: {date_str} and session_id: {session_id}")
        return {"error": "Chat history not found."}
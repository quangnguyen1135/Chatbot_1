import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
import json

# Initialize Firebase Admin SDK only if it hasn't been initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase/chatbot-df502-firebase-adminsdk-56sbd-48189d1535.json')
    initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def main():
    def fetch_all_dates():
        """Fetch all unique dates from Firebase Firestore."""
        dates = []
        try:
            chat_history_ref = db.collection('chat_history').stream()
            for date_doc in chat_history_ref:
                date = date_doc.id
                dates.append(date)  # The date is already in string format
            return dates
        except Exception as e:
            st.error(f"An error occurred while fetching dates: {e}")
            return []

    def fetch_all_session_ids_for_date(date_str):
        """Fetch all session IDs for a specific date from Firebase Firestore."""
        all_sessions = []
        try:
            chat_history_ref = db.collection('chat_history').document(date_str).get()
            if chat_history_ref.exists:
                data = chat_history_ref.to_dict()
                sessions = data.get("sessions_id", {})
                for session_id in sessions.keys():
                    all_sessions.append(session_id)
            return all_sessions
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return []

    def format_session_id(session_id):
        """Format session ID from HHMMSS to HH:MM:SS."""
        return f"{session_id[:2]}:{session_id[2:4]}:{session_id[4:]}"

    def fetch_chat_history(date_str, session_id):
        """Fetch chat history from Firebase Firestore."""
        try:
            chat_doc_ref = db.collection('chat_history').document(date_str).get()
            if chat_doc_ref.exists:
                data = chat_doc_ref.to_dict()
                sessions = data.get("sessions_id", {})
                if session_id in sessions:
                    return sessions[session_id]
                else:
                    st.error(f"Chat history not found for session {session_id} on date {date_str}.")
                    return {"error": "Chat history not found."}
            else:
                st.error(f"No chat history found for date: {date_str}")
                return {"error": "No chat history found."}
        except Exception as e:
            st.error(f"An error occurred while fetching chat history: {e}")
            return {"error": str(e)}

    def download_chat_history(history, date_str, session_id):
        """Download chat history as a text file."""
        try:
            history_str = json.dumps(history, indent=4)
            st.download_button(
                label="Download Chat History",
                data=history_str,
                file_name=f"chat_history_{date_str}_{session_id}.json",
                mime="application/json"
            )
        except Exception as e:
            st.error(f"An error occurred while preparing the download: {e}")

    st.title("Chat History Viewer")

    # Fetch dates and display in a select box
    dates = fetch_all_dates()
    if dates:
        selected_date = st.selectbox("Select a Date", dates)

        if selected_date:
            # Fetch sessions for the selected date and display in another select box
            sessions = fetch_all_session_ids_for_date(selected_date)
            if sessions:
                st.subheader("Search time")
                search_session_query = st.text_input("Enter time search keyword:")
                if search_session_query:
                    sessions = [sid for sid in sessions if search_session_query in sid]

                formatted_sessions = {format_session_id(sid): sid for sid in sessions}
                selected_formatted_session = st.selectbox("Select a Time", sorted(formatted_sessions.keys(), key=lambda x: formatted_sessions[x]))
                selected_session = formatted_sessions[selected_formatted_session]

                if selected_session:
                    # Fetch and display chat history for the selected session
                    history = fetch_chat_history(selected_date, selected_session)
                    if "error" in history:
                        st.error(history["error"])
                    else:
                        st.subheader("Search Chat History")
                        search_query = st.text_input("Enter search keyword:")

                        st.subheader("Chat History")
                        search_results = []
                        # Enumerate through messages to prepend session number
                        for i, msg in enumerate(history.get("messages", []), start=1):
                            role = msg.get('role', 'user')  # Default to 'user' if role is not specified
                            content = msg.get('content', '')
                            timestamp = msg.get('timestamp', '')

                            # Check if search query matches content
                            if search_query.strip().lower() in content.strip().lower():
                                search_results.append((role, content, timestamp))
                        if search_results:
                            # Display search results
                            for i, (role, content, timestamp) in enumerate(search_results, start=1):
                                if role == "user":
                                    with st.chat_message('user'):
                                        st.markdown(f"**User**: {content}  \n *{timestamp}*")
                                elif role == "assistant":
                                    with st.chat_message('assistant'):
                                        st.markdown(f"{content}  \n *{timestamp}*")
                        else:
                            st.markdown("No matching content found.")
                        download_chat_history(history, selected_date, selected_session)

if __name__ == "__main__":
    main()

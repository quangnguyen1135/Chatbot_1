import streamlit as st
import os
import requests
from datetime import datetime
import time

def generate_response_words(response):
    """Generator function to yield each word in the response."""
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.02)

# Load API token from environment variables
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTU2NTYxNTgsInN1YiI6ImV4YW1wbGVfdXNlciJ9.Ecm4-6ZvUu37h7KXfDtgPISY2qiTWxIsjWiMUS65_zQ"

def main():
    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
        with st.chat_message('assistant'):
            st.markdown("Bạn có câu hỏi gì không ?")
    if "response_stream" not in st.session_state:
        st.session_state.response_stream = ""
    if "suggestion_clicked" not in st.session_state:
        st.session_state.suggestion_clicked = False
    if "session_id" not in st.session_state:
        # Generate a new session_id if it is not present
        now = datetime.now()
        session_id = now.strftime("%H%M%S")
        st.session_state.session_id = session_id

    # Display past messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        if role == "user":
            with st.chat_message('user'):
                st.markdown(content)
        elif role == "assistant":
            with st.chat_message('assistant'):
                st.markdown(content)

    # Handle user input
    if st.session_state.suggestion_clicked:
        user_question = st.session_state.suggestion_text
        st.session_state.suggestion_clicked = False
    else:
        user_question = st.chat_input(placeholder="Hãy nhập yêu cầu của bạn!", key="user_input")
        
            
    if user_question:
        with st.chat_message('user'):
            st.markdown(user_question)
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message('assistant'):
            with st.spinner('Chờ chút nha 😉'):
                data_input = {
                    "user_input": user_question,
                    "session_id": st.session_state.session_id
                }
                url = "http://127.0.0.1:8000/chat_bot_api"
                headers = {
                    "Authorization": f"Bearer {API_TOKEN}",
                    "Content-Type": "application/json"
                }
                response_api = requests.post(url, json=data_input, headers=headers)
                response = ""
                if response_api.status_code == 200:
                    try:
                        response = response_api.json().get("response", "")
                        if not response.strip():
                            response = "Câu hỏi của bạn không rõ ràng. Vui lòng nhập lại hoặc cung cấp thêm thông tin."
                    except requests.exceptions.JSONDecodeError:
                        response = "Có lỗi xảy ra khi xử lý phản hồi từ server."
                else:
                    response = f"Có lỗi xảy ra: {response_api.status_code}"
                st.write_stream(generate_response_words(response))
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(f'<div id="latest_message"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <script>
                document.getElementById('latest_message').scrollIntoView();
                document.querySelector('input[type="text"]').focus();
            </script>
            """,
            unsafe_allow_html=True
        )
        st.experimental_rerun()

if __name__ == "__main__":
    main()
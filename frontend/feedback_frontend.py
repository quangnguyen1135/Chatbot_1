import streamlit as st 
from backend.account_backend import save_report

def main():
    st.title('Report Issue :bug:')
    if st.session_state.logged_in:
            email = st.session_state.email
            issue = st.text_area('Describe the issue you encountered')
            if st.button('Submit Report'):
                save_report(email, issue)
                st.success('Report submitted successfully. Thank you for your feedback!')
    else:
        st.error('Please log in to report an issue.')
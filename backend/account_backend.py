import streamlit as st
import pyrebase
from firebase_admin import firestore, auth
import requests

db = firestore.client()

# Firebase configuration
Config = {
    'apiKey': "AIzaSyCVWqqSbCHQ0FYQsXuldDkWXX_rybYq-2k",
    'authDomain': "chatbot-df502.firebaseapp.com",
    'projectId': "chatbot-df502",
    'storageBucket': "chatbot-df502.appspot.com",
    'messagingSenderId': "1030299526853",
    'appId': "1:1030299526853:web:b3562e2670e379d86ef2ac",
    'measurementId': "G-DR2NGFB201",
    'databaseURL': "https://user.firebaseio.com"
}

firebase = pyrebase.initialize_app(Config)
auth = firebase.auth()
storage = firebase.storage()

def main():
    def login(email, password):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            uid = user['localId']
            role = get_user_role(uid)

            if role in [0, 1]:
                st.info('Login successful!')
                st.session_state.logged_in = True  # Set login state
                st.session_state.role = role       # Store the role in session state
                st.session_state.email = email  
                st.session_state.status= status # Store the email in session state
                st.experimental_set_query_params(logged_in=True)
                st.experimental_rerun()
            else:
                st.error('Login failed. Your account does not have permission to login.')
        except Exception as e:
            st.error(f'Login failed. Please check your credentials. {e}')

    def get_user_role(uid):
        try:
            doc_ref = db.collection('accounts').document(uid)
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict().get('role', 0)
            else:
                return 0
        except Exception as e:
            st.error(f'Failed to get user role: {e}')
            return 0

    def forget_password(email):
        try:
            auth.send_password_reset_email(email)
            st.success("Password reset email sent successfully.")
        except Exception as e:
            st.error(f'Password reset failed: {e}')

    def app():
        st.title('Welcome to CANAWAN-CHAT :sunglasses:')
        email = st.text_input('Email Address')
        password = st.text_input('Password', type='password')
        if st.button('Login'):
            login(email, password)
        if st.button('Forgot Password?'):
            forget_password(email)

    app()

def email_exists_in_database(email):
    try:
        collection_ref = db.collection('accounts')
        query = collection_ref.where('email', '==', email).get()
        if len(query) > 0:
            return True
        else:
            return False
    except Exception as e:
        st.error(f'Failed to check email existence: {e}')
        return True

def signup():
    st.title('Create account for user :sunglasses:')
    name = st.text_input('Full Name')
    email = st.text_input('Email Address')
    password = st.text_input('Password', type='password')
    role = st.selectbox('Role', [0, 1])  # 0 for admin, 1 for user
    avatar = st.file_uploader('Upload Avatar', type=['png', 'jpg', 'jpeg'])
    
    if st.button('Signup'):
        try:
            if email_exists_in_database(email):
                st.error('This email address is already registered. Please use a different one.')
            else:
                user = auth.create_user_with_email_and_password(email, password)
                uid = user['localId']
                
                if avatar is not None:
                    avatar_url = upload_avatar(uid, avatar)
                else:
                    avatar_url = None
                
                save_account(name, email, uid, role, avatar_url)
                st.success('Sign up successful! Please login.')
        except Exception as e:
            st.error(f'Sign up failed. Please try again. {e}')

def save_account(name, email, uid, role, avatar_url):
    try:
        collection_ref = db.collection('accounts')
        doc_ref = collection_ref.document(uid)
        doc_ref.set({
            'name': name,
            'email': email,
            'role': role,
            'avatar_url': avatar_url
        })
    except Exception as e:
        st.error(f'Failed to save account information. Please try again. {e}')

def upload_avatar(uid, avatar):
    try:
        storage = firebase.storage()
        avatar_path = f'avatars/{uid}.png'
        storage.child(avatar_path).put(avatar)
        avatar_url = storage.child(avatar_path).get_url(None)
        return avatar_url
    except Exception as e:
        st.error(f'Failed to upload avatar: {e}')
        return None

def save_report(email, issue):
    try:
        collection_ref = db.collection('reports')
        collection_ref.add({
            'email': email,
            'issue': issue,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        st.error(f'Failed to submit report: {e}')


def update_user_password(uid, current_email, current_password, new_password):
    try:
        # Reauthenticate the user
        user = auth.sign_in_with_email_and_password(current_email, current_password)
        id_token = user['idToken']

        # Check if new password is the same as current password
        if new_password == current_password:
            raise Exception('New password must be different from the current password.')

        # Update password if changed
        if new_password:
            response = requests.post(
                'https://identitytoolkit.googleapis.com/v1/accounts:update',
                params={'key': Config['apiKey']},
                json={'idToken': id_token, 'password': new_password, 'returnSecureToken': True}
            )
            if response.status_code != 200:
                error_message = response.json().get('error', {}).get('message', 'Unknown error')
                if error_message == 'INVALID_PASSWORD':
                    raise Exception('Current password is incorrect.')
                else:
                    raise Exception(error_message)
        return True
    except Exception as e:
        if 'INVALID_PASSWORD' in str(e):
            st.error('Current password is incorrect.')  # Thông báo lỗi mật khẩu hiện tại không đúng
        else:
            st.error(f'Failed to update user details: {e}')  # Xử lý các lỗi khác
        return False

def update_user_details(uid, new_name, new_avatar_url):
    try:
        db = firestore.client()
        collection_ref = db.collection('accounts')
        doc_ref = collection_ref.document(uid)
        
        # Prepare update data
        update_data = {}
        if new_name:
            update_data['name'] = new_name
        if new_avatar_url:
            update_data['avatar_url'] = new_avatar_url
        
        # Perform update
        doc_ref.update(update_data)
        
        return True
    except Exception as e:
        st.error(f'Failed to update user details: {e}')
        return False
    
def get_user_details(email):
    try:
        collection_ref = db.collection('accounts')
        query = collection_ref.where('email', '==', email).get()
        if query:
            user_details = query[0].to_dict()
            user_details['uid'] = query[0].id
            return user_details
        else:
            return None
    except Exception as e:
        st.error(f'Failed to retrieve user details: {e}')
        return None

def upload_image_to_storage(file):
    try:
        # Upload file to Firebase Storage
        filename = file.name
        storage.child("images/" + filename).put(file)

        # Get URL of the uploaded file
        url = storage.child("images/" + filename).get_url(None)
        return url
    except Exception as e:
        st.error(f"Failed to upload image: {e}")
        return None
    
def load_all_reports():
    try:
        collection_ref = db.collection('reports')
        query = collection_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).get()
        reports = []
        for doc in query:
            report_data = doc.to_dict()
            report_data['id'] = doc.id
            reports.append(report_data)

        return reports
    except Exception as e:
        st.error(f'Failed to load reports: {e}')
        return []

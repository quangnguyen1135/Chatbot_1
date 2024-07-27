import streamlit as st
from backend.account_backend import update_user_details ,get_user_details , upload_image_to_storage, update_user_password

def main():
    if st.session_state.logged_in:
        user_details = get_user_details(st.session_state.email)
        if user_details:
            st.title('User Profile')
            st.image(user_details.get('avatar_url', 'https://via.placeholder.com/100'), width=100)
            st.write(f"Name: {user_details.get('name')}")
            st.write(f"Email: {user_details.get('email')}")
            st.write(f"Role: {'Admin' if user_details.get('role') == 0 else 'User'}")
            st.write(f"User ID (uid): {user_details['uid']}")

            # Edit Profile Information
            if st.button('Edit Profile'):
                st.title('Update Profile Information')

                # Input fields for updating profile
                with st.form(key='update_form'):
                    new_name = st.text_input('New Name', user_details.get('name'))
                    uploaded_file = st.file_uploader("Choose a new avatar image", type=["jpg", "jpeg", "png"])
                    submit_button = st.form_submit_button(label='Update')

                    if uploaded_file:
                        avatar_url = upload_image_to_storage(uploaded_file)
                    else:
                        avatar_url = user_details.get('avatar_url', 'https://via.placeholder.com/100')

                    if submit_button:
                        update_successful = update_user_details(user_details['uid'], new_name, avatar_url)

                        if update_successful:
                            st.success('Profile updated successfully!')
                            st.session_state.name = new_name  # Update session state
                        else:
                            st.error('Failed to update profile.')


            # Change Password
            with st.expander('Change Password', expanded=False):
                current_email = user_details.get('email')
                current_password = st.text_input('Current Password', type='password')
                new_password = st.text_input('New Password', type='password')
                confirm_password = st.text_input('Confirm New Password', type='password')
                if new_password == confirm_password:
                    if st.button('Update Password'):
                        update_successful = update_user_password(user_details['uid'], current_email,current_password, new_password)
                        if update_successful:
                            st.success('Password updated successfully!')
                        else:
                            st.error('Failed to update password.')
                else:
                    st.error('Passwords do not match.')

            # Logout
            if st.button('Logout'):
                st.session_state.logged_in = False
                st.experimental_set_query_params(logged_in=False)
                st.experimental_rerun()
        else:
            st.error('Failed to retrieve user details.')
    else:
        st.error('Please log in to report an issue.')

if __name__ == "__main__":
    main()

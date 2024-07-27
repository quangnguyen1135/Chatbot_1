import streamlit as st
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
from frontend import chat_bot_frontend, history_page, create_vector_db , user_frontend , feedback_frontend , view_reports_frontend
from backend import account_backend

# Load environment variables
load_dotenv()

# Set page title
st.set_page_config(page_title="CHAT BOT CANAWAN")

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Embed Google Analytics tracking code
st.markdown(
    f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={os.getenv('analytics_tag')}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{os.getenv('analytics_tag')}');
    </script>
    """, unsafe_allow_html=True
)

# Define a class for multiple apps
class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        # Sidebar menu
        with st.sidebar:
            if st.session_state.logged_in:
                role = st.session_state.get('role', 1)
                if role == 0:
                    apps = option_menu(
                        menu_title="Main Menu",
                        options=['Chat Bot', "History", "User", "Create account","View reports","DB Settings"],
                        icons=['chat-fill', 'info-circle-fill', 'user', 'user'],
                        menu_icon='chat-text-fill',
                        default_index=0,
                        styles={
                            "container": {"padding": "10px", "background-color": "#f0f0f0", "border-radius": "5px"},
                            "icon": {"color": "#007bff", "font-size": "20px"},
                            "nav-link": {"color": "#007bff", "font-size": "18px", "text-align": "left", "margin": "5px", "padding": "5px"},
                            "nav-link-selected": {"background-color": "#007bff", "color": "#fff"},
                        }
                    )
                else:
                    apps = option_menu(
                        menu_title="Main Menu",
                        options=['Chat Bot', "User" ,"Feedback"],
                        icons=['chat-fill', 'user','feedback'],
                        menu_icon='chat-text-fill',
                        default_index=0,
                        styles={
                            "container": {"padding": "10px", "background-color": "#f0f0f0", "border-radius": "5px"},
                            "icon": {"color": "#007bff", "font-size": "20px"},
                            "nav-link": {"color": "#007bff", "font-size": "18px", "text-align": "left", "margin": "5px", "padding": "5px"},
                            "nav-link-selected": {"background-color": "#007bff", "color": "#fff"},
                        }
                    )
            else:
                apps = option_menu(
                    menu_title="Main Menu",
                    options=["Login"],
                    icons=['chat-fill', 'user', 'user'],
                    menu_icon='chat-text-fill',
                    default_index=0,
                    styles={
                        "container": {"padding": "10px", "background-color": "#f0f0f0", "border-radius": "5px"},
                        "icon": {"color": "#007bff", "font-size": "20px"},
                        "nav-link": {"color": "#007bff", "font-size": "18px", "text-align": "left", "margin": "5px", "padding": "5px"},
                        "nav-link-selected": {"background-color": "#007bff", "color": "#fff"},
                    }
                )

        # Display selected app based on user choice
        if apps == "Chat Bot":
            st.title("Chat Bot Canawan")
            chat_bot_frontend.main()
        elif apps == "History":
            history_page.main()
        elif apps == "DB Settings":
            create_vector_db.main()
        elif apps == "Login":
            account_backend.main()
        elif apps == "User":
            user_frontend.main()
        elif apps == "Create account":
            account_backend.signup()
        elif apps == "Feedback":
            feedback_frontend.main()
        elif apps == "View reports":
            view_reports_frontend.main()    
    
# Create an instance of MultiApp
multi_app = MultiApp()

# Add apps to the MultiApp instance
multi_app.add_app("Chat Bot", chat_bot_frontend.main)
multi_app.add_app("History", history_page.main)
multi_app.add_app("Custom DB", create_vector_db.main)

# Run the selected app
multi_app.run()

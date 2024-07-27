# Chat Bot

This repository contains the code for a chatbot application designed for Cawana company. It consists of two main components: a Streamlit-based user interface for interacting with the chatbot and a FastAPI backend for handling user input and managing chat history.

## Usage

### Running the Streamlit Chatbot Interface

1. **Install the enviroment:**

    ```
    python -m venv venv
    ```
2. **Navigate to the project directory and activate the virtual environment:**

    ```
    .venv\Scripts\activate
    ```
3.**Install requirements:**

    ```
    pip install -r rq.txt
    ```

4. **Start the Streamlit application to launch the chatbot interface:**

    ```
    streamlit run main.py
    ```

### Running the FastAPI Backend

1. **Activate the virtual environment:**

    ```
    venv\Scripts\activate
    ```

2. **Start the FastAPI server using Uvicorn:**

    ```
    uvicorn api:app
    ```

## API DOCUMENTATION

### Endpoints

- **POST /chat_bot_api:** Handle user input and return a response from the chatbot.
- **GET /chat_bot_responses:** Get all responses from the chatbot.


### Usage

- **POST /chat_bot_api:** Send a POST request with a JSON body containing "user_input" and "session_id" fields to interact with the chatbot. Example:

    ```json
    {
        "user_input": "Hello!",
        "session_id":"123"
    }
    ```

- **GET /chat_bot_responses:** Send a GET request to retrieve all responses from the chatbot.

### Dependencies

- python: 3.x
- streamlit: Latest version
- uvicorn: Latest version
- fastapi: Latest version
- firebase-admin: Latest version
- python-dotenv: Latest version
- pydantic: Latest version

Make sure to install these dependencies before running the application.

import jwt
from datetime import datetime, timedelta

# Define a secret key (should be securely generated and managed)
SECRET_KEY = "your_secret_key_here"

# Define expiration time for the token (e.g., 1 hour from now)
expires_delta = timedelta(hours=1)
expires_at = datetime.utcnow() + expires_delta

# Define token data (e.g., user information or permissions)
token_data = {"sub": "example_user"}

# Encode the token
token = jwt.encode({"exp": expires_at, **token_data}, SECRET_KEY, algorithm="HS256")

print("Token:", token)

import streamlit as st
import os
import json
import urllib.request
import urllib.error
import ssl
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def allow_self_signed_https(allowed: bool):
    """
    Bypass server certificate verification if using self-signed certificates.
    """
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

# If you're using self-signed certificates, enable this:
allow_self_signed_https(True)

# Retrieve environment variables
api_key = os.getenv("API_KEY")
endpoint = os.getenv("ENDPOINT")

# Validate that the API key and endpoint are available
if not api_key:
    st.error("API_KEY is not set. Please update your .env file.")
    st.stop()

if not endpoint:
    st.error("ENDPOINT is not set. Please update your .env file.")
    st.stop()

def call_api(input_text: str) -> dict:
    """
    Calls the API endpoint with the provided input text.
    The request sends a JSON payload with a single key "text".
    """
    # Prepare the payload data (adjust the structure as required by your API)
    data = {
        "text": input_text
    }
    # Convert payload to JSON and encode to bytes
    body = str.encode(json.dumps(data))

    # Prepare request headers with authentication
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + api_key
    }

    # Create the request object
    req = urllib.request.Request(endpoint, body, headers)

    try:
        with urllib.request.urlopen(req) as response:
            result = response.read()
            # Decode the result assuming JSON response; adjust as needed
            return json.loads(result.decode('utf-8'))
    except urllib.error.HTTPError as error:
        error_message = f"The request failed with status code: {error.code}\n"
        error_message += f"Headers: {error.info()}\n"
        error_message += f"Error response: {error.read().decode('utf8', 'ignore')}"
        return {"error": error_message}
    except Exception as e:
        return {"error": str(e)}

# --- Streamlit App UI ---

st.title("Simple API Caller")

# Create a text input box
user_input = st.text_input("Enter text to send to the API:")

# Create a submit button
if st.button("Submit"):
    if user_input:
        st.info("Sending data to API...")
        response = call_api(user_input)
        st.write("Response from API:")
        st.json(response)
    else:
        st.warning("Please enter some text before submitting.")

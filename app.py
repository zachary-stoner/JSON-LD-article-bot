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

# Enable bypass for self-signed certificates if necessary
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

def call_api(input_url: str) -> dict:
    """
    Calls the API endpoint with the provided input URL.
    The request sends a JSON payload with 'chat_history' as an empty list and 'URL' with the user input.
    """
    # Prepare the payload with the required keys:
    # - Use an empty list for chat_history instead of an empty string.
    data = {
        "chat_history": [],
        "URL": input_url
    }
    # Convert the payload to JSON and encode it to bytes
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
            # Decode the result assuming it's a JSON response
            return json.loads(result.decode('utf-8'))
    except urllib.error.HTTPError as error:
        error_message = f"The request failed with status code: {error.code}\n"
        error_message += f"Headers: {error.info()}\n"
        error_message += f"Error response: {error.read().decode('utf8', 'ignore')}"
        return {"error": error_message}
    except Exception as e:
        return {"error": str(e)}

# --- Streamlit App UI ---

st.title("Article JSON-LD Generator")

# Create a text input box for the URL
user_url = st.text_input("Enter the URL to process: Please note this is only intended for article ")

# Create a submit button
if st.button("Submit"):
    if user_url:
        st.info("Scraping URL and generating JSON-LD...")
        response = call_api(user_url)
        st.write("Response from API:")
        st.json(response)
    else:
        st.warning("Please enter a URL before submitting.")

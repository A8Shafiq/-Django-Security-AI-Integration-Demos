import requests # Import library to make HTTP requests
import json     # Import library to handle JSON data

# =========================================================================
# LLM INTEGRATION UTILITY (DEMO FOR STUDENTS)
# =========================================================================
# This file handles the communication between the Django app and AI models.
# =========================================================================

# SETTINGS (Real apps use .env files for secrets!)
OPENAI_API_KEY = "your_openai_api_key_here" # Placeholder for OpenAI key
GEMINI_API_KEY = "your_gemini_api_key_here" # Placeholder for Google Gemini key

# --- OLLAMA SETTINGS (Local AI) ---
OLLAMA_URL = "http://localhost:11434/api/generate" # The local API endpoint for Ollama
OLLAMA_MODEL = "llama3.1:latest"                 # The name of the model installed on your PC

# CONFIGURATION SWITCHES
MOCK_MODE = False   # Set to True to simulate AI without an internet or server connection
USE_OLLAMA = True   # Set to True to prioritize your local Ollama instance

def get_llm_response(prompt): # Function definition that takes user text as input
    """
    Sends a prompt to an LLM and returns the text response.
    """
    
    # 1. CHECK MOCK MODE
    if MOCK_MODE: # If mock mode is active
        import time # Import time library locally
        time.sleep(1) # Wait 1 second to feel realistic
        return f"AI Response to: '{prompt}'\n\nThis is a MOCK response." # Return fake text

    # 2. OPTION: LOCAL OLLAMA (Priority)
    if USE_OLLAMA: # If we are told to use Ollama
        try: # Start error handling block
            # Prepare the data packet for Ollama
            data = {
                "model": OLLAMA_MODEL, # Specify which model to use
                "prompt": prompt,      # The actual question from the user
                "stream": False        # Get full response at once (don't stream)
            }
            # Send the request to Ollama's server on your PC
            response = requests.post(OLLAMA_URL, json=data, timeout=30)
            # Check if the connection was successful (throws error if not)
            response.raise_for_status()
            # Convert the server's raw signal into a Python data object
            result = response.json()
            # Extract the 'response' field and return it
            return result.get('response', 'No response from Ollama.')
        except Exception as e: # If something goes wrong (Ollama not running, etc.)
            # Return a helpful error message with debugging info
            return f"Error connecting to local Ollama (Model: {OLLAMA_MODEL}): {str(e)}."

    # 3. OPTION: GOOGLE GEMINI (External API)
    # The URL including the API key for Google's model
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"} # Tell server we are sending JSON
    data = { # Following Google's specific JSON structure
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try: # Start error handling for external API
        # Send post request to Google
        response = requests.post(endpoint, headers=headers, json=data, timeout=10)
        # Check for success
        response.raise_for_status()
        # Parse result
        result = response.json()
        # Navigate the nested JSON structure to get the text
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e: # Catch internet/API errors
        return f"Error connecting to AI: {str(e)}" # Return error text

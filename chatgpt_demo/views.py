from django.shortcuts import render # Tool to display HTML templates
from django.http import JsonResponse   # Tool to send data (not HTML) back to the browser
import json                           # Tool to decode text sent from JavaScript
from .utils import get_llm_response   # Import our AI utility function

# =========================================================================
# CHATGPT DEMO VIEW
# =========================================================================
def ai_chat_view(request): # The main function that handles the AI page
    """
    Handles both showing the page and processing AI messages.
    """
    # 1. HANDLE POST REQUESTS (When the user clicks 'Send')
    if request.method == 'POST': 
        try:
            # Decode the message sent by the browser's JavaScript
            data = json.loads(request.body)
            # Get the text the user typed
            user_message = data.get('message', '')

            # CALL our utility function to get a response from Ollama/API
            ai_response = get_llm_response(user_message)

            # Return the AI's reply as a JSON packet so JS can show it
            return JsonResponse({
                'status': 'success', # Tell JS everything went well
                'reply': ai_response # Give JS the actual text to show
            })
        except Exception as e:
            # If a major error happens, tell JS what went wrong
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    # 2. HANDLE GET REQUESTS (When the user first visits the link)
    # Just show the chat interface HTML file
    return render(request, 'chatgpt_demo.html')

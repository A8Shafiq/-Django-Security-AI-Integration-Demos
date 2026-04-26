from django.urls import path # Import path tool to define URLs
from . import views         # Import our views file from the same folder

# List of URL patterns for this specific app
urlpatterns = [
    # Map the root /ai/ to our ai_chat_view function
    path('', views.ai_chat_view, name='ai_chat'), # 'name' lets us link to this in HTML
]

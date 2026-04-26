from django.shortcuts import render

def home(request):
    """Render the main project landing page."""
    return render(request, 'home.html')

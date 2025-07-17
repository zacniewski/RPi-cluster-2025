from django.shortcuts import render

# Create your views here.
def dashboard(request):
    """
    View function for the monitoring dashboard.
    Displays system status information using Bulma cards with chess icons.
    """
    context = {
        'page_title': 'Dashboard',
    }
    return render(request, 'monitoring/dashboard.html', context)

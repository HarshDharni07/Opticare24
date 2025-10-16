# Simple welcome view for testing
from django.http import JsonResponse

def welcome_view(request):
    """
    Simple welcome endpoint to test Django setup
    """
    return JsonResponse({
        'message': 'Welcome to OptiCare24 API!',
        'status': 'Server running successfully',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api_auth': '/api/auth/ (coming soon)',
            'api_products': '/api/products/ (coming soon)',
            'api_orders': '/api/orders/ (coming soon)',
        }
    })
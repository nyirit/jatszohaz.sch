from django.conf import settings

def default_context_processor(request):
    return {
        'SOCIAL_AUTH_BACKEND': settings.SOCIAL_AUTH_BACKEND,
    }
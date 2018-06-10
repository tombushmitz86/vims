from django.http import HttpResponse


def health(request):
    """An endpoint that may be used for external health checks."""
    return HttpResponse('OK', status=200, content_type='text/plain')

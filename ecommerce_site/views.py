from django.http import HttpResponse
from django.template.loader import render_to_string


def robots_txt(request):
    """Serve robots.txt dynamically"""
    content = render_to_string('robots.txt', {
        'domain': request.get_host(),
    })
    return HttpResponse(content, content_type='text/plain') 
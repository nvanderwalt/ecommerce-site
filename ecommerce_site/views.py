from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render


def home_view(request):
    """Home page view"""
    return render(request, 'home.html')


def robots_txt(request):
    """Serve robots.txt dynamically"""
    content = render_to_string('robots.txt', {
        'domain': request.get_host(),
    })
    return HttpResponse(content, content_type='text/plain') 
from django.http import HttpResponse


def hello_view(request):
    html = '<html><body><p>Belajar Django itu menyenangkan.</p></body></html>'
    return HttpResponse(html)
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import City


def hello_view(request):
    html = '<html><body><p>Belajar Django itu menyenangkan.</p></body></html>'
    return HttpResponse(html)


@login_required
def city_list_view(request, state_id):
    cities = City.objects.filter(state=state_id)
    return JsonResponse({'data': [{'id': city.id, 'name': city.name} for city in cities]})

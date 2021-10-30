from django.urls import path

from .views import city_list_view


urlpatterns = [
    path('cities/<int:state_id>', city_list_view, name='get-city-list'),
]

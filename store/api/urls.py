from django.urls import path

from .views import ExampleListView

urlpatterns = [
    # contoh url untuk API endpoint
    path('example/', ExampleListView.as_view(), name='api-example'),
]

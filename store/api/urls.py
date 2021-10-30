from django.urls import path

from .views import ExampleListView, CategoryListView

urlpatterns = [
    # contoh url untuk API endpoint
    path('example/', ExampleListView.as_view(), name='api-example'),
    # API Category
    path('category', CategoryListView.as_view(), name='api-category-list'),
]

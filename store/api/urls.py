from django.urls import path

from .views import ExampleListView, CategoryListView, ProductListView, ProductDetailView

urlpatterns = [
    # contoh url untuk API endpoint
    path('example/', ExampleListView.as_view(), name='api-example'),
    # API Category
    path('category', CategoryListView.as_view(), name='api-category-list'),
    # API Product
    path('product', ProductListView.as_view(), name='api-product-list'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='api-product-detail'),
]

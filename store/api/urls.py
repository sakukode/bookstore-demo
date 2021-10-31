from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    ExampleListView,
    CategoryListView,
    ProductListView,
    ProductDetailView,
    RegisterView,
    CartListCreateView,
    CartUpdateDestroyView,
    StateListView,
    CityListView,
    ShippingCostView,
    OrderView
)

urlpatterns = [
    # contoh url untuk API endpoint
    path('example/', ExampleListView.as_view(), name='api-example'),
    # API Category
    path('category', CategoryListView.as_view(), name='api-category-list'),
    # API Product
    path('product', ProductListView.as_view(), name='api-product-list'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='api-product-detail'),
    # API Register
    path('register', RegisterView.as_view(), name='api-register'),
    # API Login
    path('login', TokenObtainPairView.as_view(), name='api-login'),
    # API Cart
    path('cart', CartListCreateView.as_view(), name='api-cart-list_create'),
    path('cart/<int:pk>', CartUpdateDestroyView.as_view(), name='api-cart-update_destroy'),
    # API State
    path('state', StateListView.as_view(), name='api-state-list'),
    # API City
    path('city', CityListView.as_view(), name='api-city-list'),
    # API Shipping Cost
    path('shipping-cost', ShippingCostView.as_view(), name='api-shipping-cost'),
    # API Order
    path('order', OrderView.as_view(), name='api-order-list-create'),
]

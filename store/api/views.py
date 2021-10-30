from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from store.models import Category, Product

from .serializers import ExampleSerializer, CategoryListSerializer, ProductListSerializer, ProductDetailSerializer

from .filters import ProductListFilter


class ExampleListView(ListAPIView):
    serializer_class = ExampleSerializer
    queryset = Category.objects.all()
    search_fields = ['name']
    ordering_fields = ['name']

    filter_backends = (
        SearchFilter,
        OrderingFilter
    )

    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]


class CategoryListView(ListAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()
    search_fields = ['name']
    ordering_fields = ['name']

    filter_backends = (
        SearchFilter,
        OrderingFilter
    )


class ProductListView(ListAPIView):
    serializer_class = ProductListSerializer
    queryset = Product.objects.all()
    ordering_fields = ['price', 'created_at']
    search_fields = ['name', 'author']
    filterset_class = ProductListFilter

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )


class ProductDetailView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()

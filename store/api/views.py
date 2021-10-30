from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from store.models import Category

from .serializers import ExampleSerializer, CategoryListSerializer


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

from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from store.models import Category

from .serializers import ExampleSerializer


class ExampleListView(ListAPIView):
    serializer_class = ExampleSerializer
    queryset = Category.objects.all()
    search_fields = ['name']
    ordering_fields = ['name']

    filter_backends = (
        SearchFilter,
        OrderingFilter
    )


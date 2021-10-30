from rest_framework.generics import ListAPIView

from store.models import Category

from .serializers import ExampleSerializer


class ExampleListView(ListAPIView):
    serializer_class = ExampleSerializer
    queryset = Category.objects.all()

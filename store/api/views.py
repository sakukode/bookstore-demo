from django.contrib.auth.models import User
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    ListCreateAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from store.models import Category, Product, Cart, State

from .serializers import (
    ExampleSerializer,
    CategoryListSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    RegisterSerializer,
    CartSerializer,
    StateListSerializer
)

from .filters import ProductListFilter
from store.helpers import convert_rupiah_to_float, rupiah_formatting


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


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class CartListCreateView(ListCreateAPIView):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = None # menonaktifkan pagination bawaan dari djangorestframework

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # mendapatkan total items/products and total amount
        itemPrices = [(convert_rupiah_to_float(dict(item)['product']['price']) * dict(item)['quantity']) for item in
                      serializer.data]
        total_amount = sum(itemPrices)
        total_item = len(itemPrices)

        response = {"meta": {"amount": rupiah_formatting(total_amount), "item": total_item},
                    "results": serializer.data}

        return Response(response)


class CartUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    permission_classes = (IsAuthenticated,)


class StateListView(ListAPIView):
    serializer_class = StateListSerializer
    queryset = State.objects.all()
    permission_classes = (IsAuthenticated,)
    search_fields = ['name']

    filter_backends = (
        SearchFilter,
    )


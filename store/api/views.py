from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.utils.translation import gettext
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    ListCreateAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from store.models import Category, Product, Cart, State, City, Order

from .serializers import (
    ExampleSerializer,
    CategoryListSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    RegisterSerializer,
    CartSerializer,
    StateListSerializer,
    CityListSerializer,
    ShippingCostFormSerializer,
    ShippingCostListSerializer,
    OrderFormSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderProofPaymentFormSerializer
)

from .filters import ProductListFilter
from store.helpers import convert_rupiah_to_float, rupiah_formatting, get_shipping_cost


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
    search_fields = ['name']
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

        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            
            # mendapatkan total items/products and total amount
            itemPrices = [(convert_rupiah_to_float(dict(item)['product']['price']) * dict(item)['quantity']) for item in
                        serializer.data]
            total_amount = sum(itemPrices)
            total_item = len(itemPrices)

            response = {"meta": {"amount": rupiah_formatting(total_amount), "item": total_item},
                        "results": serializer.data}
        else:
            response = {"meta": {"amount": rupiah_formatting(0), "item": 0},
                        "results": []}

        return Response(response)

    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)


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


class CityListView(ListAPIView):
    serializer_class = CityListSerializer
    queryset = City.objects.all()
    permission_classes = (IsAuthenticated,)
    search_fields = ['name']
    filterset_fields = ['state']

    filter_backends = (
        SearchFilter,
        DjangoFilterBackend
    )


class ShippingCostView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializerForm = ShippingCostFormSerializer(data=data)

        if serializerForm.is_valid():
            serializerFormData = serializerForm.data
            origin = serializerFormData['origin']
            destination = serializerFormData['destination']
            courier = serializerFormData['courier']
            # kalkulasi total berat dari semua produk yang ada pada cart
            weight = Cart.objects.filter(user=request.user.id).aggregate(total=Sum(F('product__weight') * F('quantity')))[
                'total']

            if weight is None:
                return Response(data={'message': gettext('Your cart is empty.')}, status=422)

            costs = get_shipping_cost(courier=courier, origin=origin, destination=destination, weight=weight)
            result = ShippingCostListSerializer(costs, many=True)

            return Response({"results": result.data})
        else:
            return Response(data={'message': gettext('Failed get shipping cost.')}, status=422)


class OrderView(ListCreateAPIView):
    serializer_class = OrderListSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderFormSerializer
        return OrderListSerializer

    def get_queryset(self):
        return Order.objects.all().filter(user=self.request.user)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)


class OrderProofPaymentView(UpdateAPIView):
    serializer_class = OrderProofPaymentFormSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)

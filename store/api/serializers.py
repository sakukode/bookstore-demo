from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.utils.translation import gettext
from django.db import transaction

from store.models import Category, Product, Cart, State, City, Shop, Order, OrderProduct, new_order_signal
from store.helpers import rupiah_formatting, generate_invoice_number, generate_payment_token


class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)


class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(read_only=True)

    def get_price(self, obj):
        formatted_price = rupiah_formatting(obj.price)

        return formatted_price

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'image', 'price',)


class ProductDetailSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(read_only=True)

    def get_price(self, obj):
        formatted_price = rupiah_formatting(obj.price)

        return formatted_price

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'image', 'price', 'description')


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name',)
        extra_kwargs = {
            'first_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": gettext("Password didn't match.")})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class CartProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(read_only=True)

    def get_price(self, obj):
        formatted_price = rupiah_formatting(obj.price)

        return formatted_price

    class Meta:
        model = Product
        fields = ('id', 'name', 'image', 'price', 'weight',)


class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(write_only=True, default=serializers.CurrentUserDefault())
    product = CartProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True, write_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'product', 'quantity', 'user', 'product_id')
        depth = 1

    def create(self, validated_data):
        try:
            cart = Cart.objects.get(product=validated_data['product_id'], user=self.context['request'].user)

            cart.quantity = validated_data['quantity']
            cart.save()
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                product=validated_data['product_id'],
                quantity=validated_data['quantity'],
                user=validated_data['user']
            )

        return cart

    def validate(self, attrs):
        request = self.context.get('request', None)
        action = getattr(request, 'method', None)

        if action == 'PUT':
            product = self.instance.product
        else:
            product = attrs['product_id']

        if product.stock <= 0:
            raise serializers.ValidationError(gettext("Product out of stock."))

        if product.stock < attrs['quantity']:
            raise serializers.ValidationError(gettext("Product doesn't have enough stock."))

        return attrs

    def update(self, instance, validated_data):
        if 'product_id' in validated_data:
            validated_data.pop('product_id', None)

        return super(CartSerializer, self).update(instance, validated_data)

    def get_fields(self, *args, **kwargs):
        fields = super(CartSerializer, self).get_fields(*args, **kwargs)
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "PUT":
            fields['product_id'].required = False

        return fields


class StateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('id', 'name',)


class CityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name',)


class ShippingCostFormSerializer(serializers.Serializer):
    origin = serializers.SerializerMethodField(read_only=True)
    destination = serializers.IntegerField(required=True)
    courier = serializers.ChoiceField(required=True, choices=Order.SHIPPING_COURIER_CHOICES)

    def get_origin(self, obj):
        shop = Shop.objects.first()

        return shop.city.id


class ShippingCostListSerializer(serializers.Serializer):
    service = serializers.CharField()
    description = serializers.CharField()
    cost = serializers.DictField()


class OrderFormSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(write_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = (
            'id', 'invoice_number', 'payment_method', 'shipping_courier', 'shipping_service',
            'customer_name', 'customer_phone', 'customer_address', 'customer_city', 'customer_state',
            'customer_postal_code', 'sub_total', 'total_shipping', 'total', 'user',)
        read_only_fields = ('id', 'invoice_number',)
        extra_kwargs = {
            'payment_method': {'write_only': True},
            'shipping_courier': {'write_only': True},
            'shipping_service': {'write_only': True},
            'customer_name': {'write_only': True},
            'customer_phone': {'write_only': True},
            'customer_address': {'write_only': True},
            'customer_city': {'write_only': True},
            'customer_state': {'write_only': True},
            'customer_postal_code': {'write_only': True},
            'total_shipping': {'write_only': True},
            'sub_total': {'write_only': True, 'required': False},
            'total': {'write_only': True, 'required': False},
        }

    def create(self, validated_data):
        carts = Cart.objects.filter(user=self.context['request'].user)

        if not carts.exists():
            raise serializers.ValidationError("Your cart is empty.")

        sub_total = sum([(cart.quantity * cart.product.price) for cart in carts])
        total = sub_total + validated_data['total_shipping']
        validated_data['sub_total'] = sub_total
        validated_data['total'] = total

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            if order:
                # simpan data detail order di table order_products
                for cart in carts:
                    order.orderproduct_set.create(
                        quantity=cart.quantity,
                        weight=cart.product.weight,
                        price=cart.product.price,
                        total=(float(cart.quantity) * cart.product.price),
                        product=cart.product
                    )
                    cart.product.stock = cart.product.stock - cart.quantity
                    cart.product.save()

                # menggenerate invoice number
                order.invoice_number = generate_invoice_number(order)

                # jika metode pembayarannya adala "online payment",
                # maka itu akan menggenerate token pembayaran dari payment gatewat Midtrans
                if order.payment_method == Order.ONLINE_PAYMENT:
                    order.payment_token = generate_payment_token(order)

                order.save()

                # hapus data cart berdasarkan user yang melakukan request
                Cart.objects.filter(user=self.context['request'].user).delete()

                # mengirim email tagihan pesanan
                transaction.on_commit(lambda: new_order_signal.send(sender=None, order=order))

                return order

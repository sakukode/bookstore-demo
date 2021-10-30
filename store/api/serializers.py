from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.utils.translation import gettext

from store.models import Category, Product
from store.helpers import rupiah_formatting


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

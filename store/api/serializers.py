from rest_framework import serializers

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

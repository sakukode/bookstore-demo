from rest_framework import serializers

from store.models import Category


class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)

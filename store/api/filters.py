from django_filters import FilterSet, ModelMultipleChoiceFilter, RangeFilter

from store.models import Category, Product


class ProductListFilter(FilterSet):
    categories = ModelMultipleChoiceFilter(queryset=Category.objects.all())
    price = RangeFilter(field_name='price', label='price')

    class Meta:
        model = Product
        fields = ['categories', 'price']

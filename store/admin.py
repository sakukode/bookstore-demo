from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext

from .forms import ShopAdminForm
from .models import Category, Shop, Product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)


class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'email', 'phone',)

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    form = ShopAdminForm

    class Media:
        js = (
            'store/scripts/shop-admin-form.js',
        )


admin.site.register(Shop, ShopAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('custom_image', 'name', 'price', 'stock', 'weight',)
    list_display_links = ('custom_image', 'name',)
    list_editable = ('price', 'stock',)
    fields = ('name', 'price', 'stock', 'weight', 'description', 'image', 'categories',)

    def custom_image(self, obj):
        if obj.image:
            return mark_safe('<img src="{url}" width={width} />'.format(
                url=obj.image.url,
                width='120'
                )
            )
        else:
            return mark_safe('<img src="{url}" width={width} />'.format(
                url='https://via.placeholder.com/120x150.png?text=No+Image',
                width='120'
                )
            )
    custom_image.short_description = gettext('image')


admin.site.register(Product, ProductAdmin)

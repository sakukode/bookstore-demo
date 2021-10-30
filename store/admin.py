from django.contrib import admin

from .models import Category, Shop
from .forms import ShopAdminForm


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

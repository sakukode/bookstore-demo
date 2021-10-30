from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext
from django.urls import path
from functools import update_wrapper

from .forms import ShopAdminForm
from .models import Category, Shop, Product, Order, OrderProduct


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


class OrderProductAdminInline(admin.TabularInline):
    model = OrderProduct
    fields = ('product', 'quantity', 'price', 'weight', 'total',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('custom_invoice_number', 'customer_name', 'status', 'shipping_tracking_number', 'payment_method',
                    'shipping_courier', 'sub_total', 'total_shipping', 'total',)
    list_filter = ('status', 'payment_method', 'shipping_courier',)
    list_editable = ('status', 'shipping_tracking_number',)
    search_fields = ('invoice_number', 'customer_name',)
    fields = (
        'invoice_number', 'purchased_at', 'status', 'customer_name', 'customer_phone', 'customer_address',
        'customer_city',
        'customer_state', 'customer_postal_code', 'payment_method', 'shipping_courier', 'shipping_tracking_number',
        'sub_total', 'total_shipping', 'total',)
    inlines = (OrderProductAdminInline,)

    def custom_invoice_number(self, obj):
        return mark_safe('<a href="{id}/detail/">{number}</a>'.format(id=obj.id, number=obj.invoice_number))

    custom_invoice_number.short_description = gettext('invoice number')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if getattr(self, '__detail_view', None):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def detail_view(self, request, object_id, form_url='', extra_context=None):
        setattr(self, '__detail_view', True)
        # Custom template for detail view
        self.change_form_template = self.change_form_template
        ret = self.changeform_view(request, object_id, form_url, extra_context)
        delattr(self, '__detail_view')
        return ret

    def get_urls(self):
        urls = super().get_urls()

        # add detail-view for the object
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        # for the detail view.
        urls[len(urls) - 1] = path('<path:object_id>/detail/', wrap(self.detail_view), name='store_order_detail')
        return urls


admin.site.register(Order, OrderAdmin)

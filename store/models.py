from django.db import models
from django.utils.translation import gettext
from django.utils.text import slugify

from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=gettext('name'))

    def __str__(self):
        return self.name;
    
    class Meta:
        db_table = 'categories'
        verbose_name = gettext('category')
        verbose_name_plural = gettext('categories')


class State(models.Model):

    class Meta:
        db_table = 'states'
        ordering = ['name']

    name = models.CharField(max_length=100, verbose_name=gettext('name'))

    def __str__(self):
        return self.name


class City(models.Model):

    class Meta:
        db_table = 'cities'
        ordering = ['name']

    name = models.CharField(max_length=100, verbose_name=gettext('name'))
    # relationship fields
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Shop(models.Model):

    class Meta:
        db_table = 'shops'
        ordering = ['id']
        verbose_name = gettext('shop')
        verbose_name_plural = gettext('shops')

    name = models.CharField(max_length=50, verbose_name=gettext('name'))
    owner = models.CharField(max_length=100, verbose_name=gettext('owner'))
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, null=True, verbose_name=gettext('phone'))
    logo = models.ImageField(upload_to='images', null=True, blank=True, verbose_name=gettext('logo'))
    address = models.TextField(null=True, blank=True, verbose_name=gettext('address'))
    postal_code = models.CharField(max_length=5, null=True, blank=True, verbose_name=gettext('postal code'))
    # relationship fields
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, verbose_name=gettext('state'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name=gettext('city'))

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        db_table = 'products'
        ordering = ['created_at']
        verbose_name = gettext('product')
        verbose_name_plural = gettext('products')

    name = models.CharField(max_length=100, verbose_name=gettext('name'))
    slug = models.SlugField(null=True, blank=True, verbose_name=gettext('slug'))
    description = models.TextField(verbose_name=gettext('description'))
    stock = models.IntegerField(verbose_name=gettext('stock'))
    weight = models.FloatField(verbose_name=gettext('weight'))
    price = models.FloatField(verbose_name=gettext('price'))
    image = models.ImageField(upload_to='images', verbose_name=gettext('image'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # relationship fields
    categories = models.ManyToManyField(Category, verbose_name=gettext('categories'))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        super(Product, self).save(*args, **kwargs)


class Order(models.Model):
    class Meta:
        db_table = 'orders'
        ordering = ('created_at',)
        verbose_name = gettext('order')
        verbose_name_plural = gettext('orders')

    MANUAL_PAYMENT = 'manual'
    ONLINE_PAYMENT = 'online'

    PAYMENT_METHOD_CHOICES = [
        (MANUAL_PAYMENT, gettext('manual transfer bank')),
        (ONLINE_PAYMENT, gettext('online')),
    ]

    JNE_COURIER = 'jne'
    TIKI_COURIER = 'tiki'
    POS_INDONESIA_COURIER = 'pos_indonesia'

    SHIPPING_COURIER_CHOICES = [
        (JNE_COURIER, 'JNE'),
        (TIKI_COURIER, 'Tiki'),
        (POS_INDONESIA_COURIER, 'Pos Indonesia'),
    ]

    PENDING_STATUS = 0
    PAID_STATUS = 1
    SHIPPED_STATUS = 2
    COMPLETED_STATUS = 3
    CANCELED_STATUS = 4

    STATUS_CHOICES = [
        (PENDING_STATUS, gettext('pending')),
        (PAID_STATUS, gettext('paid')),
        (SHIPPED_STATUS, gettext('shipped')),
        (COMPLETED_STATUS, gettext('completed')),
        (CANCELED_STATUS, gettext('canceled')),
    ]

    invoice_number = models.CharField(max_length=11, verbose_name=gettext('invoice number'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Payment method fields
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name=gettext('payment method'))
    payment_proof = models.ImageField(upload_to='images', null=True, blank=True, verbose_name=gettext('proof of payment'))
    payment_token = models.CharField(max_length=255, null=True, blank=True, verbose_name=gettext('payment token'))
    # Shipping courier fields
    shipping_courier = models.CharField(max_length=20, choices=SHIPPING_COURIER_CHOICES, verbose_name=gettext('shipping courier'))
    shipping_service = models.CharField(max_length=100, verbose_name=gettext('shipping service'))
    shipping_tracking_number = models.CharField(max_length=255, null=True, blank=True, verbose_name=gettext('tracking number'))
    # Customer Info fields
    customer_name = models.CharField(max_length=100, verbose_name=gettext('customer name'))
    customer_phone = models.CharField(max_length=20, verbose_name=gettext('customer phone'))
    customer_address = models.TextField(verbose_name=gettext('customer address'))
    customer_city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name=gettext('customer city'))
    customer_state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, verbose_name=gettext('customer state'))
    customer_postal_code = models.CharField(max_length=5, null=True, blank=True, verbose_name=gettext('customer postal code'))
    # Date fields
    purchased_at = models.DateTimeField(blank=True, null=True, verbose_name=gettext('Purchased date'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Status fields
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING_STATUS, verbose_name=gettext('status'))
    # Billing fields
    sub_total = models.FloatField(verbose_name=gettext('sub total'))
    total_shipping = models.FloatField(verbose_name=gettext('shipping rate'))
    total = models.FloatField(verbose_name=gettext('total'))

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if self.shipping_tracking_number:
            if self.shipping_tracking_number is not None:
                self.status = self.SHIPPED_STATUS

        super(Order, self).save(*args, **kwargs)


class OrderProduct(models.Model):
    class Meta:
        db_table = 'order_products'
        ordering = ['id']

    quantity = models.IntegerField(verbose_name=gettext('quantity'))
    weight = models.FloatField(verbose_name=gettext('weight'))
    price = models.FloatField(verbose_name=gettext('price'))
    total = models.FloatField(verbose_name=gettext('total'))

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=gettext('order'))
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name=gettext('product'))

    def __str__(self):
        return ''


class Cart(models.Model):
    class Meta:
        db_table = 'carts'
        ordering = ('created_at',)
        verbose_name = gettext('cart')

    quantity = models.IntegerField(verbose_name=gettext('quantity'))
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name=gettext('product'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

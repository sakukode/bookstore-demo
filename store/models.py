from django.db import models
from django.utils.translation import gettext
from django.utils.text import slugify

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

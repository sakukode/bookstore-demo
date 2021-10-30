from django.db import models
from django.utils.translation import gettext


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=gettext('name'))
    
    class Meta:
        db_table = 'categories'
        verbose_name = gettext('category')
        verbose_name_plural = gettext('categories')

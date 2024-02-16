# db/models.py

# https://abdus.dev/posts/django-orm-standalone/

from django.db import models
from manage import init_django

init_django()

class Model(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# define models here
class Order(Model):
    date=models.DateField()
    is_submitted=models.BooleanField(default=False)
    is_processed=models.BooleanField(default=False)
    signal_price = models.DecimalField(decimal_places=2, max_digits=8)
    stop_loss_price = models.DecimalField(decimal_places=2, max_digits=8)
    target_price = models.DecimalField(decimal_places=2, max_digits=8)
    ticker = models.CharField(max_length=5)

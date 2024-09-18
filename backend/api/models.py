from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # retrive only istances not deleted (deleted_at is null)
        return super().get_queryset().filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    """
    Abstract base model class inherited by other models.
    Contains base fields: created_at, updated_at and deleted_at 
    with logics for soft delete and restore mechanism.
    """
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self):
        # override delete with soft delete
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        # restore method for soft delete
        self.deleted_at = None
        self.save()

    def is_deleted(self):
        return self.deleted_at is not None


class Product(BaseModel):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name


class Order(BaseModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    date = models.DateField(db_index=True)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"Order num: {self.name}"

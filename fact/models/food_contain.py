from django.db import models
from .food import Food
from .food_category import FoodCategory

class DefaultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class FoodContain(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    food_category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = DefaultManager()

    class Meta:
        db_table = "fact_food_contain"
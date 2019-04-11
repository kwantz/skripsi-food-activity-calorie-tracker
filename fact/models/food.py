from django.db import models
from .user import User
from .food_category import FoodCategory

class DefaultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Food(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    calorie = models.FloatField()
    carbohydrate = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = DefaultManager()

    class Meta:
        db_table = "fact_food"
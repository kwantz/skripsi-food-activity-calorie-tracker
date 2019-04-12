from django.db import models
from .user import User
from .food import Food
from .meal import Meal
from .eat_time import EatTime

class DefaultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class CalorieIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, null=True)
    eat_time = models.ForeignKey(EatTime, on_delete=models.CASCADE)
    qty = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = DefaultManager()

    class Meta:
        db_table = "fact_calorie_intake"
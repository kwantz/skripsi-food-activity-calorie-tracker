from django.db import models
from .gender import Gender
from .activity_factor import ActivityFactor

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    weight = models.FloatField()
    height = models.FloatField()
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    activity_factor = models.ForeignKey(ActivityFactor, on_delete=models.CASCADE)

    class Meta:
        db_table = 'fact_user'
from django.db import models
from .user import User
from .activity_label import ActivityLabel

# class DefaultManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(deleted_at__isnull=True)

class CalorieBurnt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_label = models.ForeignKey(ActivityLabel, on_delete=models.CASCADE)
    start_track = models.DateTimeField()
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    # objects = DefaultManager()

    class Meta:
        db_table = "fact_calorie_burnt"
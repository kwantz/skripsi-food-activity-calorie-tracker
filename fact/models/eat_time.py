from django.db import models

class DefaultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class EatTime(models.Model):
    name = models.CharField(max_length=50)
    percentage = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = DefaultManager()

    class Meta:
        db_table = "fact_eat_time"
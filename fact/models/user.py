from django.db import models
from .role import Role
from .gender import Gender

class DefaultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    weight = models.FloatField()
    height = models.FloatField()
    birth_year = models.IntegerField()
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    reason_block = models.CharField(max_length=255, null=True)
    forgot_password = models.CharField(max_length=255, null=True, default=None)
    blocked_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = DefaultManager()

    class Meta:
        db_table = "fact_user"
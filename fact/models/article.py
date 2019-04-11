from django.db import models
from .user import User

class DefaultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = DefaultManager()

    class Meta:
        db_table = "fact_article"
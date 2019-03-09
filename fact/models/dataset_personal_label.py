from django.db import models
from .user import User

class DatasetPersonalLabel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'fact_dataset_personal_label'
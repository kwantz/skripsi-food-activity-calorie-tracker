from django.db import models

class Gender(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'fact_gender'
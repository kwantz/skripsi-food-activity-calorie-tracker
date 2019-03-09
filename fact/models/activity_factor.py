from django.db import models

class ActivityFactor(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'fact_activity_factor'
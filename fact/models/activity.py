from django.db import models
from .user import User
from .activity_label import ActivityLabel

class DefaultManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.ForeignKey(ActivityLabel, on_delete=models.CASCADE)

    x_axis_jitter = models.FloatField()
    x_axis_mean_crossing_rate = models.FloatField()
    x_axis_mean = models.FloatField()
    x_axis_std = models.FloatField()
    x_axis_var = models.FloatField()
    x_axis_min = models.FloatField()
    x_axis_max = models.FloatField()
    x_axis_acf_mean = models.FloatField()
    x_axis_acf_std = models.FloatField()
    x_axis_acv_mean = models.FloatField()
    x_axis_acv_std = models.FloatField()
    x_axis_skew = models.FloatField()
    x_axis_kurtosis = models.FloatField()
    x_axis_sqrt = models.FloatField()

    y_axis_jitter = models.FloatField()
    y_axis_mean_crossing_rate = models.FloatField()
    y_axis_mean = models.FloatField()
    y_axis_std = models.FloatField()
    y_axis_var = models.FloatField()
    y_axis_min = models.FloatField()
    y_axis_max = models.FloatField()
    y_axis_acf_mean = models.FloatField()
    y_axis_acf_std = models.FloatField()
    y_axis_acv_mean = models.FloatField()
    y_axis_acv_std = models.FloatField()
    y_axis_skew = models.FloatField()
    y_axis_kurtosis = models.FloatField()
    y_axis_sqrt = models.FloatField()

    z_axis_jitter = models.FloatField()
    z_axis_mean_crossing_rate = models.FloatField()
    z_axis_mean = models.FloatField()
    z_axis_std = models.FloatField()
    z_axis_var = models.FloatField()
    z_axis_min = models.FloatField()
    z_axis_max = models.FloatField()
    z_axis_acf_mean = models.FloatField()
    z_axis_acf_std = models.FloatField()
    z_axis_acv_mean = models.FloatField()
    z_axis_acv_std = models.FloatField()
    z_axis_skew = models.FloatField()
    z_axis_kurtosis = models.FloatField()
    z_axis_sqrt = models.FloatField()

    magnitude_jitter = models.FloatField()
    magnitude_mean_crossing_rate = models.FloatField()
    magnitude_mean = models.FloatField()
    magnitude_std = models.FloatField()
    magnitude_var = models.FloatField()
    magnitude_min = models.FloatField()
    magnitude_max = models.FloatField()
    magnitude_acf_mean = models.FloatField()
    magnitude_acf_std = models.FloatField()
    magnitude_acv_mean = models.FloatField()
    magnitude_acv_std = models.FloatField()
    magnitude_skew = models.FloatField()
    magnitude_kurtosis = models.FloatField()
    magnitude_sqrt = models.FloatField()

    requested_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = DefaultManager()

    class Meta:
        db_table = 'fact_activity'
# Generated by Django 2.1.7 on 2019-07-08 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fact', '0002_user_forgot_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='food',
            name='food_category',
        ),
        migrations.AddField(
            model_name='user',
            name='confirm_email',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
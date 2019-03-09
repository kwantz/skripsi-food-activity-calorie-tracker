# Generated by Django 2.1.7 on 2019-03-03 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fact', '0002_auto_20190303_1710'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityFactor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'fact_activity_factor',
            },
        ),
        migrations.CreateModel(
            name='DatasetPersonal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x_axis_jitter', models.FloatField()),
                ('x_axis_mean_crossing_rate', models.FloatField()),
                ('x_axis_mean', models.FloatField()),
                ('x_axis_std', models.FloatField()),
                ('x_axis_var', models.FloatField()),
                ('x_axis_min', models.FloatField()),
                ('x_axis_max', models.FloatField()),
                ('x_axis_acf_mean', models.FloatField()),
                ('x_axis_acf_std', models.FloatField()),
                ('x_axis_acv_mean', models.FloatField()),
                ('x_axis_acv_std', models.FloatField()),
                ('x_axis_skew', models.FloatField()),
                ('x_axis_kurtosis', models.FloatField()),
                ('x_axis_sqrt', models.FloatField()),
                ('y_axis_jitter', models.FloatField()),
                ('y_axis_mean_crossing_rate', models.FloatField()),
                ('y_axis_mean', models.FloatField()),
                ('y_axis_std', models.FloatField()),
                ('y_axis_var', models.FloatField()),
                ('y_axis_min', models.FloatField()),
                ('y_axis_max', models.FloatField()),
                ('y_axis_acf_mean', models.FloatField()),
                ('y_axis_acf_std', models.FloatField()),
                ('y_axis_acv_mean', models.FloatField()),
                ('y_axis_acv_std', models.FloatField()),
                ('y_axis_skew', models.FloatField()),
                ('y_axis_kurtosis', models.FloatField()),
                ('y_axis_sqrt', models.FloatField()),
                ('z_axis_jitter', models.FloatField()),
                ('z_axis_mean_crossing_rate', models.FloatField()),
                ('z_axis_mean', models.FloatField()),
                ('z_axis_std', models.FloatField()),
                ('z_axis_var', models.FloatField()),
                ('z_axis_min', models.FloatField()),
                ('z_axis_max', models.FloatField()),
                ('z_axis_acf_mean', models.FloatField()),
                ('z_axis_acf_std', models.FloatField()),
                ('z_axis_acv_mean', models.FloatField()),
                ('z_axis_acv_std', models.FloatField()),
                ('z_axis_skew', models.FloatField()),
                ('z_axis_kurtosis', models.FloatField()),
                ('z_axis_sqrt', models.FloatField()),
                ('magnitude_jitter', models.FloatField()),
                ('magnitude_mean_crossing_rate', models.FloatField()),
                ('magnitude_mean', models.FloatField()),
                ('magnitude_std', models.FloatField()),
                ('magnitude_var', models.FloatField()),
                ('magnitude_min', models.FloatField()),
                ('magnitude_max', models.FloatField()),
                ('magnitude_acf_mean', models.FloatField()),
                ('magnitude_acf_std', models.FloatField()),
                ('magnitude_acv_mean', models.FloatField()),
                ('magnitude_acv_std', models.FloatField()),
                ('magnitude_skew', models.FloatField()),
                ('magnitude_kurtosis', models.FloatField()),
                ('magnitude_sqrt', models.FloatField()),
            ],
            options={
                'db_table': 'fact_dataset_personal',
            },
        ),
        migrations.CreateModel(
            name='DatasetPersonalLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'dataset_personal_label',
            },
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'fact_gender',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=255)),
                ('weight', models.FloatField()),
                ('height', models.FloatField()),
                ('activity_factor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fact.ActivityFactor')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fact.Gender')),
            ],
            options={
                'db_table': 'fact_user',
            },
        ),
        migrations.AddField(
            model_name='datasetpersonallabel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fact.User'),
        ),
        migrations.AddField(
            model_name='datasetpersonal',
            name='label',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fact.DatasetPersonalLabel'),
        ),
        migrations.AddField(
            model_name='datasetpersonal',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fact.User'),
        ),
    ]

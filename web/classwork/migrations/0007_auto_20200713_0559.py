# Generated by Django 3.0.8 on 2020-07-13 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classwork', '0006_auto_20200711_0539'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='short_desc',
        ),
        migrations.AddField(
            model_name='classoffer',
            name='skip_tagline',
            field=models.CharField(blank=True, max_length=46),
        ),
        migrations.AddField(
            model_name='classoffer',
            name='skip_weeks',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='skipped mid-session class weeks'),
        ),
        migrations.AddField(
            model_name='subject',
            name='tagline_1',
            field=models.CharField(blank=True, max_length=23),
        ),
        migrations.AddField(
            model_name='subject',
            name='tagline_2',
            field=models.CharField(blank=True, max_length=23),
        ),
        migrations.AddField(
            model_name='subject',
            name='tagline_3',
            field=models.CharField(blank=True, max_length=23),
        ),
    ]

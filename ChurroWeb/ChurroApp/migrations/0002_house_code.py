# Generated by Django 2.1.1 on 2018-10-13 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChurroApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

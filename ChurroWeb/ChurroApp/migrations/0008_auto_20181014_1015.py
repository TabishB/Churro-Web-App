# Generated by Django 2.1.1 on 2018-10-14 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ChurroApp', '0007_auto_20181014_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chore',
            name='frequency',
            field=models.CharField(choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly'), ('FORTNIGHTLY', 'Fortnightly'), ('MONTHLY', 'Monthly'), ('QUARTERLY', 'Quarterly'), ('YEARLY', 'Yearly')], max_length=20),
        ),
    ]

# Generated by Django 4.2 on 2024-05-13 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationuser',
            name='is_email_verified',
            field=models.BooleanField(default=False, verbose_name='email verified'),
        ),
    ]

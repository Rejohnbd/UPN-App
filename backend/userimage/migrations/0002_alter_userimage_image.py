# Generated by Django 4.2.16 on 2024-09-25 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userimage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userimage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='./'),
        ),
    ]

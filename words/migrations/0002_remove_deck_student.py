# Generated by Django 3.0.2 on 2020-02-05 09:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deck',
            name='student',
        ),
    ]

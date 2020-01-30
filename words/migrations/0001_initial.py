# Generated by Django 3.0.2 on 2020-01-30 07:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(default='New Deck', max_length=100)),
                ('color', models.CharField(default='#00bcd4', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, upload_to='cards/')),
                ('explanation', models.TextField(blank=True, max_length=500)),
                ('translation', models.CharField(blank=True, max_length=55)),
                ('synonymes', models.TextField(blank=True, max_length=255)),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='words.Deck')),
            ],
        ),
    ]

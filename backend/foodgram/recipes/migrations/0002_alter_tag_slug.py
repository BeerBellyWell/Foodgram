# Generated by Django 4.2.1 on 2023-05-19 23:21

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='name', verbose_name='Slug тега'),
        ),
    ]

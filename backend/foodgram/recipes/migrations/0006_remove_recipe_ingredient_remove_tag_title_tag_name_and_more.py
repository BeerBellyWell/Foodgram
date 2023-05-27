# Generated by Django 4.2.1 on 2023-05-21 00:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_rename_name_tag_title_alter_tag_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='title',
        ),
        migrations.AddField(
            model_name='tag',
            name='name',
            field=models.CharField(default='name', max_length=50, unique=True, verbose_name='Название тега'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ForeignKey(choices=[('Завтрак', 'Breakfast'), ('Обед', 'Lunch'), ('Ужин', 'Dinner')], on_delete=django.db.models.deletion.CASCADE, to='recipes.tag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Slug тега'),
        ),
    ]

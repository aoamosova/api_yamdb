# Generated by Django 2.2.16 on 2022-06-05 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20220605_2019'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='reviews',
            name='uniq_reviews_title_author',
        ),
    ]
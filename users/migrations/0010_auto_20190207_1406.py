# Generated by Django 2.0.3 on 2019-02-07 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20190207_1342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labels',
            name='note_id',
        ),
        migrations.AddField(
            model_name='labels',
            name='note_id',
            field=models.ManyToManyField(blank=True, null=True, to='users.Notes'),
        ),
    ]

# Generated by Django 2.0.3 on 2019-02-07 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_labels_note_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='labels',
            name='note_id',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
from __future__ import absolute_import
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    """Adds image_caption and lead text fields to the Entry model in the Zinnia application."""
    dependencies = [
        ('zinnia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='image_caption',
            field=models.TextField(
                help_text="Image's caption.",
                verbose_name='caption', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entry',
            name='lead',
            field=models.TextField(
                help_text='Lead paragraph',
                verbose_name='lead', blank=True),
            preserve_default=False,
        ),
    ]

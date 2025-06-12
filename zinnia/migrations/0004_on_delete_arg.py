from __future__ import absolute_import
from django.db import migrations
from django.db import models
import mptt.fields


class Migration(migrations.Migration):
    """
    Alters the 'parent' field in the 'Category' model to support MPTT-based hierarchy.
    """
    dependencies = [
        ('zinnia', '0003_publication_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=mptt.fields.TreeForeignKey(
                blank=True, null=True,
                on_delete=models.SET_NULL,
                related_name='children', to='zinnia.Category',
                verbose_name='parent category'),
        ),
    ]

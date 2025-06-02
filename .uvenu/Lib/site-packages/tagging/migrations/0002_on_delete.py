import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('tagging', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taggeditem',
            name='content_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='contenttypes.ContentType',
                verbose_name='content type'),
        ),
        migrations.AlterField(
            model_name='taggeditem',
            name='tag',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='tagging.Tag',
                verbose_name='tag'),
        ),
    ]

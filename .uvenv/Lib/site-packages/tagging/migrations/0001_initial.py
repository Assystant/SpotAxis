from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    unique=True, max_length=50,
                    verbose_name='name', db_index=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
        ),
        migrations.CreateModel(
            name='TaggedItem',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(
                    verbose_name='object id', db_index=True)),
                ('content_type', models.ForeignKey(
                    verbose_name='content type',
                    on_delete=models.SET_NULL,
                    to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(
                    related_name='items', verbose_name='tag',
                    on_delete=models.SET_NULL,
                    to='tagging.Tag')),
            ],
            options={
                'verbose_name': 'tagged item',
                'verbose_name_plural': 'tagged items',
            },
        ),
        migrations.AlterUniqueTogether(
            name='taggeditem',
            unique_together=set([('tag', 'content_type', 'object_id')]),
        ),
    ]

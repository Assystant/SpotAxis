# -*- coding: utf-8 -*-


from __future__ import absolute_import
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    """
    Migration to create the QueueMembership model linking users to authorized queues.

    This migration depends on the Django user model (which may be swappable) and a
    previous helpdesk migration '0003_initial_data_import'. It defines a new model
    `QueueMembership` that associates a user with one or more helpdesk queues they
    are authorized to access.

    Attributes:
        dependencies (list): List of migration dependencies that must be applied before this migration.
        operations (list): List of migration operations, here creating the QueueMembership model.

    Model: QueueMembership
    Fields:
        id (AutoField): Primary key for the model, automatically created.
        queues (ManyToManyField): Many-to-many relationship to the 'Queue' model, representing authorized queues.
        user (OneToOneField): One-to-one relationship to the user model, representing the user owning this membership.

    Meta Options:
        verbose_name (str): Human-readable singular name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
    """


    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('helpdesk', '0003_initial_data_import'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueueMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('queues', models.ManyToManyField(to='helpdesk.Queue', verbose_name='Authorized Queues')),
                ('user', models.OneToOneField(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Queue Membership',
                'verbose_name_plural': 'Queue Memberships',
            },
            bases=(models.Model,),
        ),
    ]

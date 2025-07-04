# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-10-11 19:34


from __future__ import absolute_import
from django.db import migrations, models

"""
Migration to add the 'referal_type' field to the ExternalReferal model.

Details:
- Adds a CharField named 'referal_type' with a max length of 2.
- The field has choices: 'JB' (Job Board) and 'ER' (External Referer).
- The default value is set to 'JB'.
- This field categorizes the type of external referral source.
"""

class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0022_auto_20171011_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalreferal',
            name='referal_type',
            field=models.CharField(choices=[('JB', 'Job Board'), ('ER', 'External Referer')], default='JB', max_length=2),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django import forms
import os
from django.utils.translation import gettext as _
from candidates.models import *
from django import forms
from common.fields import MultiFileField

# select_text = _(u'Select' + '...')
# select_option = _(u"Select an option")
# initial_country = Country.objects.get(iso2_code__exact='MX')


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         widgets = {
#             'image': AjaxClearableFileInput
#         }

# class UploadForm(forms.Form):
#     attachments = MultiFileField(min_num=1, max_num=5, max_file_size=1024*1024*5, required=False, label=_(u'Support files or referece to the job.'))



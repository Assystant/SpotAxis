from __future__ import absolute_import
import uuid

from django import forms
import unicodedata

from upload_logos.models import UploadedFile


class UploadedFileForm(forms.ModelForm):

    class Meta:
        model = UploadedFile
        fields = ('file',)

    def clean_file(self):
        data = self.cleaned_data['file']
        # Change the name of the file to something unguessable
        # Eliminates accents and other special characters in file name
        name = ''.join((c for c in unicodedata.normalize('NFD', data.name) if unicodedata.category(c) != 'Mn'))
        # Construct the new name as <unique-hex>-<name>.<ext>
        data.name = '%s-%s' % (uuid.uuid4().hex, name)
        return data
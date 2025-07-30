# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.db import models
from django.utils.translation import gettext_lazy as _

from upload_logos.settings import FILE_FIELD_MAX_LENGTH


class UploadedFile(models.Model):
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    file = models.ImageField(_('file'), max_length=FILE_FIELD_MAX_LENGTH, upload_to='preuploads/')

    def delete(self, *args, **kwargs):
        super(UploadedFile, self).delete(*args, **kwargs)
        if self.file:
            self.file.delete()
    delete.alters_data = True

    def __str__(self):
        return str(self.file)

    class Meta:
        ordering = ('-creation_date',)
        verbose_name = _('Logo Upload')
        verbose_name_plural = _('Logos Uploads')

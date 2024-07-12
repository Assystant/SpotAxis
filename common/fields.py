# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import os
import unicodedata
import uuid
import datetime

class MultiFileInput(forms.FileInput):
    def render(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super(MultiFileInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            value = files.get(name)
            if isinstance(value, list):
                return value
            else:
                return [value]


class MultiFileField(forms.FileField):
    widget = MultiFileInput
    default_error_messages = {
        'min_num': _(u'El minimo de archivos es de s %(min_num).'),
        'max_num': _(u'Ha superado el maximo de archivos permitidos por carga (5 archivos).'),
        'file_size': _(u' %(uploaded_file_name)s supera el tamaño maximo permitido (5 Mb).'),
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('max_file_size', None)
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            i = super(MultiFileField, self).to_python(item)
            if i:
                ret.append(i)
        return ret

    def validate(self, data):
        super(MultiFileField, self).validate(data)
        num_files = len(data)
        valid_extensions = ['.pdf','.PDF','.doc','.DOC','.docx','.DOCX','.jpg','.JPG','.jpeg','.JPEG','.png','.PNG','.xlsx','.XLSX','.xls','.XLS','.ppt','.PPTX']
        if len(data) and not data[0]:
            num_files = 0
        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})
        for uploaded_file in data:
            if self.maximum_file_size and uploaded_file.size > self.maximum_file_size:
                raise ValidationError(self.error_messages['file_size'] % {'uploaded_file_name': uploaded_file.name})
            ext = os.path.splitext(uploaded_file.name)[1]  # [0] returns path+filename
            name = os.path.splitext(uploaded_file.name)[0]
            if ext in valid_extensions:
                # Se eliminan los acentos y otros caracteres especiales del nombre de la imagen
                name = ''.join((c for c in unicodedata.normalize('NFD',name) if unicodedata.category(c) != 'Mn'))
                uploaded_file.name = u'%s-%s%s' % (name, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"), ext)
            else:
                raise ValidationError(u'Tipo de archivo no soportado.')


class SingleFileField(forms.FileField):
    widget = MultiFileInput
    default_error_messages = {
        'min_num': _(u'El minimo de archivos es de s %(min_num).'),
        'max_num': _(u'Solo puedes subir un archivo.'),
        'file_size': _(u' %(uploaded_file_name)s supera el tamaño maximo permitido (20 Mb).'),
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('max_file_size', None)
        super(SingleFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            i = super(SingleFileField, self).to_python(item)
            if i:
                ret.append(i)
        return ret

    def validate(self, data):
        super(SingleFileField, self).validate(data)
        num_files = len(data)
        valid_extensions = ['.pdf','.PDF','.doc','.DOC','.docx','.DOCX']
        if len(data) and not data[0]:
            num_files = 0
        if num_files < self.min_num:
            raise ValidationError(self.error_messages['min_num'] % {'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(self.error_messages['max_num'] % {'max_num': self.max_num, 'num_files': num_files})
        for uploaded_file in data:
            if self.maximum_file_size and uploaded_file.size > self.maximum_file_size:
                raise ValidationError(self.error_messages['file_size'] % {'uploaded_file_name': uploaded_file.name})
            ext = os.path.splitext(uploaded_file.name)[1]  # [0] returns path+filename
            name = os.path.splitext(uploaded_file.name)[0]
            if ext in valid_extensions:
                # Se eliminan los acentos y otros caracteres especiales del nombre de la imagen
                name = ''.join((c for c in unicodedata.normalize('NFD',name) if unicodedata.category(c) != 'Mn'))
                uploaded_file.name = u'%s-%s%s' % (name, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"), ext)
            else:
                raise ValidationError(u'Tipo de archivo no soportado.')


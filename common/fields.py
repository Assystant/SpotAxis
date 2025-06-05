"""
Django custom form fields and widgets for handling file uploads.

This module provides specialized form fields and widgets for handling single and multiple
file uploads in Django applications. It includes validation for file size, number of files,
and file extensions, as well as file name sanitization.

Classes:
    - MultiFileInput: A widget for handling multiple file uploads
    - MultiFileField: A form field for handling multiple file uploads with validation
    - SingleFileField: A form field for handling single file uploads with validation
"""

# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
import unicodedata
import uuid
import datetime

class MultiFileInput(forms.FileInput):
    """
    A custom widget that extends Django's FileInput to handle multiple file uploads.
    
    This widget adds the 'multiple' attribute to the file input element, allowing
    users to select multiple files in the file selection dialog.
    """
    
    def render(self, name, value, attrs=None):
        """
        Render the widget with multiple file upload capability.
        
        Args:
            name (str): The name of the form field
            value: The value of the form field
            attrs (dict): Additional HTML attributes for the widget
            
        Returns:
            str: The rendered HTML for the widget
        """
        attrs['multiple'] = 'multiple'
        return super(MultiFileInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        """
        Extract the files from the POST data.
        
        Args:
            data (dict): POST data
            files (dict): Files data
            name (str): Field name
            
        Returns:
            list: List of uploaded files
        """
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            value = files.get(name)
            if isinstance(value, list):
                return value
            else:
                return [value]


class MultiFileField(forms.FileField):
    """
    A form field for handling multiple file uploads with validation.
    
    This field allows uploading multiple files and includes validation for:
    - Minimum and maximum number of files
    - Maximum file size
    - Allowed file extensions
    - File name sanitization
    
    Attributes:
        min_num (int): Minimum number of required files
        max_num (int): Maximum number of allowed files
        maximum_file_size (int): Maximum allowed file size in bytes
        valid_extensions (list): List of allowed file extensions
    """
    
    widget = MultiFileInput
    default_error_messages = {
        'min_num': _(u'El minimo de archivos es de s %(min_num).'),
        'max_num': _(u'Ha superado el maximo de archivos permitidos por carga (5 archivos).'),
        'file_size': _(u' %(uploaded_file_name)s supera el tamaño maximo permitido (5 Mb).'),
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize the MultiFileField with custom parameters.
        
        Args:
            min_num (int): Minimum number of files required (default: 0)
            max_num (int): Maximum number of files allowed (default: None)
            max_file_size (int): Maximum file size in bytes (default: None)
        """
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('max_file_size', None)
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        """
        Convert the uploaded files data to Python objects.
        
        Args:
            data (list): List of uploaded files
            
        Returns:
            list: List of processed file objects
        """
        ret = []
        for item in data:
            i = super(MultiFileField, self).to_python(item)
            if i:
                ret.append(i)
        return ret

    def validate(self, data):
        """
        Validate the uploaded files.
        
        Performs validation on:
        - Number of files (min/max)
        - File size
        - File extensions
        - Sanitizes file names
        
        Args:
            data (list): List of files to validate
            
        Raises:
            ValidationError: If validation fails
        """
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
    """
    A form field for handling single file uploads with validation.
    
    Similar to MultiFileField but restricted to single file uploads and
    with a more limited set of allowed file extensions. Includes validation for:
    - File count (max 1)
    - Maximum file size
    - Allowed file extensions (PDF and DOC formats only)
    - File name sanitization
    
    Attributes:
        min_num (int): Minimum number of required files
        max_num (int): Maximum number of allowed files (default: 1)
        maximum_file_size (int): Maximum allowed file size in bytes
        valid_extensions (list): List of allowed file extensions
    """
    
    widget = MultiFileInput
    default_error_messages = {
        'min_num': _(u'El minimo de archivos es de s %(min_num).'),
        'max_num': _(u'Solo puedes subir un archivo.'),
        'file_size': _(u' %(uploaded_file_name)s supera el tamaño maximo permitido (20 Mb).'),
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize the SingleFileField with custom parameters.
        
        Args:
            min_num (int): Minimum number of files required (default: 0)
            max_num (int): Maximum number of files allowed (default: None)
            max_file_size (int): Maximum file size in bytes (default: None)
        """
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('max_file_size', None)
        super(SingleFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        """
        Convert the uploaded file data to Python objects.
        
        Args:
            data (list): List containing the uploaded file
            
        Returns:
            list: List with the processed file object
        """
        ret = []
        for item in data:
            i = super(SingleFileField, self).to_python(item)
            if i:
                ret.append(i)
        return ret

    def validate(self, data):
        """
        Validate the uploaded file.
        
        Performs validation on:
        - File count (must be 1)
        - File size
        - File extension (PDF or DOC formats only)
        - Sanitizes file name
        
        Args:
            data (list): List containing the file to validate
            
        Raises:
            ValidationError: If validation fails
        """
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


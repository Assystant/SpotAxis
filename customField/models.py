from __future__ import unicode_literals

from companies.models import Company
from customField.settings import ALLOWED_FORM_FIELDS, TEMPLATE_MANAGER, ALLOWED_FORM_WIDGETS
from django.db import models
from django.template.loader import render_to_string

# Create your models here.
class FieldClassification(models.Model):
    """
    This model stores classification labels for the various :model:`customField.FieldType` objects. It also controls which labels are visible to end users and which ones require options to be entered for user input.
    """
    
    name = models.CharField(verbose_name="Label", max_length=50, unique=True)
    is_visible = models.BooleanField(verbose_name="Is Visible?", blank=True, default=True)
    requires_options = models.BooleanField(verbose_name="Requires Options?", blank=True, default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Field Classification"
        verbose_name_plural = "Field Classifications"

    def __str__(self):
        return self.name

def form_fields_as_choices():
    """
    Returns a list of form fields available for selection
    """
    fields = []
    fields = [(field[0],field[0]) if len(field) == 1 else (fields[0],field[1]) for field in ALLOWED_FORM_FIELDS ]
    return fields

def form_widgets_as_choices():
    """
    Returns a list of form widgets available for selection
    """
    widgets = []
    widgets = [(widget[0],widget[0]) if len(widget) == 1 else (widgets[0],widget[1]) for widget in ALLOWED_FORM_WIDGETS ]
    return widgets

class FieldType(models.Model):
    """
    This model stores various field types that are available for users to be used as :model:`customField.Field` while creating forms. The objects are related to :model:`customField.FieldClassification` and form fields as defined in settings. The field types can be disabled if not required and labelled to be more user friendly. If a label is not provided, the default name of the form fields's widget will be used.
    """
    
    name = models.CharField(verbose_name="Label", max_length=50, null=True, blank=True)
    classification = models.ForeignKey(FieldClassification, verbose_name="Classification", null=True, blank=True, default=None)
    is_enabled = models.BooleanField(verbose_name="Is Enabled?", blank=True, default=True)
    form_field = models.CharField(verbose_name='Inbuilt Field', max_length=50, choices=form_fields_as_choices(), default = None)
    field_widget = models.CharField(verbose_name='Inbuilt Widget', max_length=50, choices=form_widgets_as_choices(), default = None)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Field Type"
        verbose_name_plural = "Field Types"

    def __str__(self):
        return self.name.strip() or self.form_field

class Template(models.Model):
    """
    This model combines various :model:`customField.Field`s together into a single template with an identifier label.
    """

    name = models.CharField(verbose_name="Label", max_length=50, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    belongs_to = models.ForeignKey(Company, null=True, blank=True, default=None)
    # created_by = models.ForeignKey(TEMPLATE_MANAGER)

    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"

    def __str__(self):
        return self.name

    def rendered_form(self, preview= False):
        from customField.forms import TemplatedForm
        form = TemplatedForm(template = self,formClasses='form-control')
        return render_to_string('templated_form.html',{'form':form, 'preview':preview})

    def has_required_fields(self):
        required = False
        for field in self.field_set.all():
            required |= field.is_required
        return required
    
class Field(models.Model):
    """
    This model stores the various fields created by users and is identified by a label which is also used as the placeholder. If the :model:`customField.FieldType` requires options, they are retrieved from :model:`customForm.Option`. User also has the flexibility to choose wether a field is required.
    """

    name = models.CharField(verbose_name="Label", max_length=50, null=True, blank=True)
    field_type = models.ForeignKey(FieldType, verbose_name='Field Type')
    is_required = models.BooleanField(verbose_name="Is Required?", blank=True, default=False)
    template = models.ForeignKey(Template)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(TEMPLATE_MANAGER)

    class Meta:
        verbose_name = "Field"
        verbose_name_plural = "Fields"

    def __str__(self):
        return self.name or str(self.field_type)
    
class Option(models.Model):
    """
    This model stores options to be used by :model:`customField.Field` if it's :model:`customField.FieldClassification` requires options.
    """

    name = models.CharField(verbose_name="Field Option", max_length=50)
    field = models.ForeignKey(Field, related_name="field_option")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(TEMPLATE_MANAGER)

    class Meta:
        verbose_name = "Option"
        verbose_name_plural = "Options"

    def __str__(self):
        return self.name

class FieldValue(models.Model):
    """
    This model stores End User Values filled for :model:`customField.Field`s in :model:`customField.Template`s .
    """

    field = models.ForeignKey(Field)
    value = models.CharField(null=True, blank=True, default="", max_length=50)

    class Meta:
        verbose_name = "FieldValue"
        verbose_name_plural = "FieldValues"

    def __str__(self):
        return self.value.strip() or "NA"
    

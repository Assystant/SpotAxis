"""
Django forms and formsets for managing custom fields, options, and templates.

Includes:
- FieldForm: For custom field input.
- OptionForm: For options tied to fields.
- TemplateForm: For naming templates.
- Custom nested formset logic for managing nested fields and options.
- TemplatedForm: Runtime-generated form based on a template instance.
"""

from __future__ import absolute_import
from customField.models import *
from django import forms
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet, inlineformset_factory, ModelForm
from nested_formset import *

class FieldForm(BaseNestedModelForm):
    """
        Form for creating or editing a Field model instance, including nested options if required.

        Fields:
            - name: Label for the field.
            - field_type: Reference to a FieldType instance.
            - is_required: Whether the field must be filled by a user.
        """
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':'Field Label',
                                      'class': 'form-control'}),
        max_length=50,
        min_length=2,
        required = True,
        error_messages={'required': "Enter the Field name"},
    )

    field_type = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        queryset=FieldType.objects.all(),
        initial=1
    )
    is_required = forms.BooleanField(
        label='Is Required?',
        widget=forms.CheckboxInput(attrs={'class': ""}),
        initial=False,
        required=False,
    )
    def clean_name(self):
        """
            Validates and cleans the 'name' field by trimming whitespace.
        """
        name = self.cleaned_data.get('name')
        if not name.strip():
            raise forms.ValidationError(code = 'required')
        return name.strip()
    class Meta:
        model = Field
        fields = ['name','field_type', 'is_required',]   

class OptionForm(ModelForm):
    """
        Form for creating or editing an Option associated with a Field.
    """
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':'Option',
                                      'class': 'form-control'}),
        max_length=50,
        min_length=2,
        error_messages={'required': "Enter the Option value"},
        required=True,
    )

    class Meta:
        model = Option
        fields = ['name']
    
class TemplateForm(ModelForm):
    """
        Form for naming a Template that groups Fields together.
    """
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder':'Untitled Template',
                                      'class': 'form-control'}),
        max_length=50,
        min_length=2,
        error_messages={'required': "Enter the Template name"},
    )

    class Meta:
        model = Template
        fields = ['name',]

def nestedformset_factory(parent_model, model, nested_formset,
                          form=BaseNestedModelForm,
                          formset=BaseNestedFormset, fk_name=None,
                          fields=None, exclude=None, extra=3,
                          can_order=False, can_delete=True,
                          max_num=None, formfield_callback=None,
                          widgets=None, validate_max=False,
                          localized_fields=None, labels=None,
                          help_texts=None, error_messages=None,
                          min_num=None, validate_min=None):
    """
    Creates a nested formset for handling hierarchical form data (e.g., fields and their options).

    Parameters:
        - parent_model: The model to which child model is related.
        - model: The child model.
        - nested_formset: The nested formset class to use.
        - Other standard formset_factory kwargs.

    Returns:
        A nested inline formset class.
    """

    kwargs = {
        'form': form,
        'formset': formset,
        'fk_name': fk_name,
        'fields': fields,
        'exclude': exclude,
        'extra': extra,
        'can_order': can_order,
        'can_delete': can_delete,
        'max_num': max_num,
        'formfield_callback': formfield_callback,
        'widgets': widgets,
        'validate_max': validate_max,
        'localized_fields': localized_fields,
        'labels': labels,
        'help_texts': help_texts,
        'error_messages': error_messages,
        'min_num': min_num,
        'validate_min': validate_min,
    }

    if kwargs['fields'] is None and form==BaseNestedModelForm:
        kwargs['fields'] = [
            field.name
            for field in model._meta.local_fields
        ]

    NestedFormSet = inlineformset_factory(
        parent_model,
        model,
        **kwargs
    )
    NestedFormSet.nested_formset_class = nested_formset

    return NestedFormSet

class BaseOptionFormset(BaseInlineFormSet):
    """
    Custom formset for validating Option entries.

    Validates:
        - Duplicate option names are not allowed.
    """

    def __init__(self, *args, **kwargs):
        super(BaseOptionFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
    def clean(self):
        """
        Ensures no duplicate option names exist in the formset.
        """

        if any(self.errors):
            return
        options = {}
        for index, form in enumerate(self.forms):
            cleaned_data = form.clean()
            if cleaned_data:
                option_label = cleaned_data['name']
                if option_label in options:
                    options[option_label] += [index]
                else:
                    options[option_label] = [index]

        for option in options:
            indexes = options[option]
            if len(indexes) > 1:
                for index in indexes:
                    self.forms[index].add_error('name', 'Duplicate options')

    def structure(self):
        """
        Renders the empty form HTML structure for dynamic front-end insertion.
        """
        structure_html = ""
        with self.empty_form as subform:
            structure_html += '<div class="formset-form" id="option-formset-structure">'
            for field in subform:
                structure_html += str(field.label)
                structure_html += str(field)
            structure_html += '<a class="formset-delete" href="javascript:void(0)">&times; Remove Option</a>'
            structure_html += '</div>'
        return structure_html

OptionFormset = inlineformset_factory(Field,Option,form = OptionForm, formset=BaseOptionFormset, extra=0, can_delete=True)

class BaseFieldFormset(BaseNestedFormset):
    """
    Custom nested formset for handling fields and their options.

    Validates:
        - Duplicate field names.
        - Required options if field type requires them.
    """

    def __init__(self, *args, **kwargs):
        super(BaseFieldFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
    def clean(self):
        """
        Validates field names for uniqueness and ensures required options are provided.
        """
        fields = {}
        for index,form in enumerate(self.forms):
            cleaned_data = form.clean()
            if cleaned_data:
                import pdb
                # pdb.set_trace()
                field_label = cleaned_data.get('name','')
                field_type = cleaned_data.get('field_type','')
                # if not field_label:
                #     form.add_error('name','Field Label is required')
                # raise forms.ValidationError(form.errors['name'] = 'Error')
                if field_label in fields:
                    fields[field_label] += [index]
                else:
                    fields[field_label] = [index]
                if field_type and field_type.classification.requires_options:
                    if not len(form.nested.forms):
                        form.add_error('field_type', 'Requires at least 1 option to be added')
        for field in fields:
            indexes = fields[field]
            if field and len(indexes) > 1:
                for index in indexes:
                    self.forms[index].add_error('name', 'Duplicate fields')



    def structure(self):
        """
        Returns HTML structure for empty field form, including nested options.
        """
        structure_html = ""
        with formset.empty_form as form:
            structure_html += '<div class="formset-form" id="field-formset-structure" '
            if form.nested:
                structure_html += "data-nested='true'"
            structure_html += ">  "
            for field in form:
                structure_html += str(field.label)
                structure_html += str(field)
            structure_html += '<div class="formset-row" data-template="#option-formset-structure" style="display:none;">'
            structure_html += str(form.nested.management_form)
            structure_html += '<input type="hidden" class="prefix" value="' + str(form.nested.prefix) + '">'
            structure_html += form.nested.structure()
            for subform in form.nested:
                structure_html += str(subform.errors)
                structure_html += '<div class="formset-form">'
                for field in subform:
                    structure_html += str(field.label)
                    structure_html += str(field)
                structure_html += '<a class="formset-delete" href="javascript:void(0)">&times; Remove Option</a>'
                structure_html += '</div>'
            structure_html += '<div class="buttonRow">'
            structure_html += '<a class="formset-add" href="javascript:void(0);">Add Option</a>'
            structure_html += '</div>'
            structure_html += '<a class="text-danger formset-delete" href="javascript:void(0)">&times; Remove Field</a>'
            structure_html += '</div>'
        return structure_html

    def templated_form(self, formClasses=None):
        """
        Generates a Django form dynamically using the formset data.

        Args:
            formClasses (str): Optional CSS classes for form styling.

        Returns:
            A dynamic Django Form instance or a message if no template is bound.
        """
        form = TemplatedForm()
        if self.is_bound:
            counter = 0
            for field in self.forms:
                try:
                    field_type = FieldType.objects.get(id=int(field.data.get('field_set-'+str(counter)+'-field_type',0)))
                except:
                    field_type = None
                if field_type:
                    formField = eval("django.forms." + str(field_type.form_field))
                    if field_type.field_widget:
                        formWidget = eval("django.forms." + str(field_type.field_widget))
                    else:
                        formWidget = None
                    form.fields[field.data.get("field_set-"+str(counter)+'-name',"")] = formField()
                    if formWidget:
                        form.fields[field.data.get("field_set-"+str(counter)+'-name',"")].widget = formWidget()
                    if formClasses:
                        form.fields[field.data.get("field_set-"+str(counter)+'-name',"")].widget.attrs['class'] = formClasses
                    if field_type.classification.requires_options:
                        fieldChoices = ()
                        subcounter = 0
                        for option in field.nested:
                            fieldChoices += ((str(subcounter+1), option.data['field_set-'+str(counter)+'-field_option-'+str(subcounter)+'-name']),)
                            subcounter += 1
                        form.fields[field.data.get("field_set-"+str(counter)+'-name',"")].choices = fieldChoices
                        if form.fields[field.data.get("field_set-"+str(counter)+'-name',"")].widget.__class__ != forms.Select and form.fields[field.data.get("field_set-"+str(counter)+'-name',"")].widget.__class__ != forms.SelectMultiple:
                            form.fields[field.data.get("field_set-"+str(counter)+'-name',"")].widget.attrs['class'] = ""
                    
                    try:
                        required = field.data['field_set-'+str(counter)+'-is_required']
                    except:
                        required = False
                    form.fields[field.data.get("field_set-"+str(counter)+'-name',"")].required = required
                counter += 1
            return form
        else:
            return "No Template Available"
        pass


    def save(self, commit=True):
        """
        Saves the formset and all nested formsets.

        Args:
            commit (bool): Whether to commit the changes to the database.

        Returns:
            The saved result of the parent formset.
        """

        result = super(BaseNestedFormset, self).save(commit=commit)

        for form in self.forms:
            if not self._should_delete_form(form) :
                form.nested.save(commit=commit)

        return result
FieldFormset = nestedformset_factory(Template,Field,nested_formset=OptionFormset, form=FieldForm, formset=BaseFieldFormset, extra=0, can_delete=True)


class TemplatedForm(forms.Form):
    """
    This is the form that will be genrated for the end user to fill. It requires a compulsary **template** parameter which is an instance of :model:`customField.Template`.
    The saving of the form creates and returns the list of :model:`customField.FieldValue` objects mapped with their correponding :model:`customField.Field` and user entered value pairs.
    """

    """
    Dynamically generated form based on a `Template` instance.

    - Populates fields based on related Field and Option models.
    - Can be rendered and saved as FieldValue objects.

    Attributes:
        template (Template): The template this form is based on.
    """

    template = None
    # TODO: Define form fields here
    def __init__(self, *args, **kwargs):
        """
        Initialising the custom :form:`customField.TemplatedForm` with and instance of :model:`customField.Template`. The form populates all the  :model:`customField.Field`s mapped to the template object along with :model:`customField.Option` as choices whereever the field is a base/derived instance of :form:`django.SelectField`.
        """

        """
        Initializes the form based on the given `template` instance and renders
        all associated fields with proper widgets, choices, and validation.
        """

        template = kwargs.pop('template', None)
        formClasses = kwargs.pop('formClasses', None)
        super(TemplatedForm, self).__init__(*args, **kwargs)
        self.template = template
        if template:
            for field in template.field_set.all():
                formField = eval("django.forms." + str(field.field_type.form_field))
                if field.field_type.field_widget:
                    formWidget = eval("django.forms." + str(field.field_type.field_widget))
                else:
                    formWidget = None
                self.fields[field.name] = formField()
                if formWidget:
                    self.fields[field.name].widget = formWidget()
                if formClasses:
                    self.fields[field.name].widget.attrs['class'] = formClasses
                if field.field_type.classification.requires_options:
                    fieldChoices = ()
                    for option in field.field_option.all():
                        fieldChoices += ((option.id, option.name),)
                    self.fields[field.name].choices = fieldChoices
                    if self.fields[field.name].widget.__class__ != forms.Select and self.fields[field.name].widget.__class__ != forms.SelectMultiple:
                        self.fields[field.name].widget.attrs['class'] = ""
                        
                self.fields[field.name].required = field.is_required

    def clean(self):
        """
        Cleans the custom :form:`customField.TemplatedForm`'s choice values by returning it's display value in cleaned data or a string of comma seperated list in case of multiselect fields.
        """
        """
        Cleans choice fields by resolving stored choice values to their display names.
        Supports both single and multiple select inputs.
        """

        for field in self.fields:
            if hasattr(self.fields[field],'choices'):
                data = self.cleaned_data[field]
                if isinstance(data,list):
                    d = ','.join([dict(self.fields[field].choices)[int(data_bit)] for data_bit in data])
                    self.cleaned_data[field] = d
                else:
                    self.cleaned_data[field] = dict(self.fields[field].choices)[int(data)]
    def save(self):
        """
        Save the :form:`customField.TemplatedForm` and return a list of the created :model:`custonField.FieldValue` objects.
        """
        """
        Saves the filled form as a list of `FieldValue` model instances.

        Returns:
            List of created FieldValue objects.
        """

        field_set = []
        for field in self.template.field_set.all():
            data = self.cleaned_data[field.name]
            field_set.append(FieldValue.objects.create(field = field, value = data))
        return field_set
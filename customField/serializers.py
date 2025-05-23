from rest_framework import serializers
from .models import (
    FieldClassification, FieldType, Template, Field,
    Option, FieldValue
)


class FieldClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldClassification
        fields = '__all__'


class FieldTypeSerializer(serializers.ModelSerializer):
    classification = FieldClassificationSerializer(read_only=True)
    classification_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldClassification.objects.all(), source='classification', write_only=True, required=False
    )

    class Meta:
        model = FieldType
        fields = [
            'id', 'name', 'classification', 'classification_id', 'is_enabled',
            'form_field', 'field_widget', 'created_on', 'updated_on'
        ]


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'name', 'field', 'created_on', 'updated_on']


class FieldSerializer(serializers.ModelSerializer):
    field_type = FieldTypeSerializer(read_only=True)
    field_type_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldType.objects.all(), source='field_type', write_only=True
    )
    options = OptionSerializer(source='field_option', many=True, read_only=True)

    class Meta:
        model = Field
        fields = [
            'id', 'name', 'field_type', 'field_type_id', 'is_required',
            'template', 'created_on', 'updated_on', 'options'
        ]


class TemplateSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(source='field_set', many=True, read_only=True)
    belongs_to_name = serializers.CharField(source='belongs_to.name', read_only=True)

    class Meta:
        model = Template
        fields = [
            'id', 'name', 'created_on', 'updated_on', 'belongs_to',
            'belongs_to_name', 'fields'
        ]


class FieldValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)

    class Meta:
        model = FieldValue
        fields = ['id', 'field', 'field_name', 'value']

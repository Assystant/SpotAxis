from rest_framework import serializers
from customField.models import FieldClassification, FieldType, Template, Field, Option, FieldValue


class FieldClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldClassification
        fields = [
            'id', 'name', 'is_visible', 'requires_options',
            'created_on', 'updated_on'
        ]
        read_only_fields = ['id', 'created_on', 'updated_on']


class FieldTypeSerializer(serializers.ModelSerializer):
    classification = FieldClassificationSerializer(read_only=True)
    classification_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldClassification.objects.all(),
        source='classification',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = FieldType
        fields = [
            'id', 'name', 'classification', 'classification_id',
            'is_enabled', 'form_field', 'field_widget',
            'created_on', 'updated_on'
        ]
        read_only_fields = ['id', 'created_on', 'updated_on']


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'name', 'field', 'created_on', 'updated_on']
        read_only_fields = ['id', 'created_on', 'updated_on']


class FieldSerializer(serializers.ModelSerializer):
    field_type = FieldTypeSerializer(read_only=True)
    field_type_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldType.objects.all(),
        source='field_type',
        write_only=True
    )
    options = OptionSerializer(source='field_option', many=True, read_only=True)

    class Meta:
        model = Field
        fields = [
            'id', 'name', 'field_type', 'field_type_id',
            'is_required', 'template', 'created_on', 'updated_on',
            'options'
        ]
        read_only_fields = ['id', 'created_on', 'updated_on', 'options']


class FieldValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)
    field = FieldSerializer(read_only=True)
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(),
        source='field',
        write_only=True
    )

    class Meta:
        model = FieldValue
        fields = ['id', 'field', 'field_id', 'field_name', 'value', 'created_on']
        read_only_fields = ['id', 'field_name', 'created_on']


class TemplateSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)
    rendered_form = serializers.SerializerMethodField()
    belongs_to_name = serializers.CharField(source='belongs_to.name', read_only=True)

    class Meta:
        model = Template
        fields = [
            'id', 'name', 'belongs_to', 'belongs_to_name',
            'fields', 'rendered_form', 'created_on', 'updated_on'
        ]
        read_only_fields = [
            'id', 'belongs_to_name', 'rendered_form',
            'created_on', 'updated_on'
        ]

    def get_rendered_form(self, obj):
        """Get the rendered form HTML"""
        return obj.rendered_form(preview=True) 
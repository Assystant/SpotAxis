from rest_framework import serializers
from .models import (
    FieldClassification, FieldType, Template, Field,
    Option, FieldValue
)
from .api.serializers import (
    FieldClassificationSerializer as APIFieldClassificationSerializer,
    FieldTypeSerializer as APIFieldTypeSerializer,
    FieldSerializer as APIFieldSerializer,
    TemplateSerializer as APITemplateSerializer,
    OptionSerializer as APIOptionSerializer,
    FieldValueSerializer as APIFieldValueSerializer
)

# Re-export API serializers for backward compatibility
FieldClassificationSerializer = APIFieldClassificationSerializer
FieldTypeSerializer = APIFieldTypeSerializer
FieldSerializer = APIFieldSerializer
TemplateSerializer = APITemplateSerializer
OptionSerializer = APIOptionSerializer
FieldValueSerializer = APIFieldValueSerializer

# Add any additional general-purpose serializers here if needed
# These would be serializers that are not API-specific and might be used
# in other parts of the application

from rest_framework import serializers
from helpdesk.models import (
    Queue, Ticket, FollowUp, TicketChange, Attachment,
    PreSetReply, EscalationExclusion, EmailTemplate,
    KBCategory, KBItem, SavedSearch, UserSettings,
    IgnoreEmail, TicketCC, CustomField,
    TicketCustomFieldValue, TicketDependency
)

class QueueSerializer(serializers.ModelSerializer):
    from_address = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = '__all__' + ('from_address',)

    def get_from_address(self, obj):
        return obj.from_address


class TicketSerializer(serializers.ModelSerializer):
    get_assigned_to = serializers.SerializerMethodField()
    ticket = serializers.SerializerMethodField()
    ticket_for_url = serializers.SerializerMethodField()
    get_priority_img = serializers.SerializerMethodField()
    get_priority_css_class = serializers.SerializerMethodField()
    get_status = serializers.SerializerMethodField()
    ticket_url = serializers.SerializerMethodField()
    staff_url = serializers.SerializerMethodField()
    can_be_resolved = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__' + (
            'get_assigned_to', 'ticket', 'ticket_for_url',
            'get_priority_img', 'get_priority_css_class',
            'get_status', 'ticket_url', 'staff_url', 'can_be_resolved'
        )

    def get_get_assigned_to(self, obj):
        return obj.get_assigned_to

    def get_ticket(self, obj):
        return obj.ticket

    def get_ticket_for_url(self, obj):
        return obj.ticket_for_url

    def get_get_priority_img(self, obj):
        return obj.get_priority_img

    def get_get_priority_css_class(self, obj):
        return obj.get_priority_css_class

    def get_get_status(self, obj):
        return obj.get_status

    def get_ticket_url(self, obj):
        return obj.ticket_url

    def get_staff_url(self, obj):
        return obj.staff_url

    def get_can_be_resolved(self, obj):
        return obj.can_be_resolved


class FollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = '__all__'


class TicketChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketChange
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'


class PreSetReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = PreSetReply
        fields = '__all__'


class EscalationExclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscalationExclusion
        fields = '__all__'


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = '__all__'


class KBCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = KBCategory
        fields = '__all__'


class KBItemSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    class Meta:
        model = KBItem
        fields = '__all__' + ('score',)

    def get_score(self, obj):
        return obj.score


class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = '__all__'


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = '__all__'


class IgnoreEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = IgnoreEmail
        fields = '__all__'


class TicketCCSerializer(serializers.ModelSerializer):
    email_address = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()

    class Meta:
        model = TicketCC
        fields = '__all__' + ('email_address', 'display')

    def get_email_address(self, obj):
        return obj.email_address

    def get_display(self, obj):
        return str(obj.display)


class CustomFieldSerializer(serializers.ModelSerializer):
    choices_as_array = serializers.SerializerMethodField()

    class Meta:
        model = CustomField
        fields = '__all__' + ('choices_as_array',)

    def get_choices_as_array(self, obj):
        return obj.choices_as_array


class TicketCustomFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCustomFieldValue
        fields = '__all__'


class TicketDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketDependency
        fields = '__all__'

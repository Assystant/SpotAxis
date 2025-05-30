from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from helpdesk import settings as helpdesk_settings

class HelpAPIView(LoginRequiredMixin, TemplateView):
    """
    View for the API help documentation page.
    """
    template_name = 'helpdesk/help_api.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['helpdesk_settings'] = helpdesk_settings
        return context

class HelpContextView(LoginRequiredMixin, TemplateView):
    """
    View for the help context documentation page.
    """
    template_name = 'helpdesk/help_context.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['helpdesk_settings'] = helpdesk_settings
        return context

class SystemSettingsView(LoginRequiredMixin, TemplateView):
    """
    View for the system settings page.
    """
    template_name = 'helpdesk/system_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['helpdesk_settings'] = helpdesk_settings
        # Add any additional context needed for system settings
        return context 
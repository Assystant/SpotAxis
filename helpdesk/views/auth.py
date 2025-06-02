from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

class HelpdeskLoginView(auth_views.LoginView):
    """
    Custom login view for the helpdesk that provides the necessary context.
    """
    template_name = 'helpdesk/registration/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context

class HelpdeskLogoutView(auth_views.LogoutView):
    """
    Custom logout view for the helpdesk that handles redirection.
    """
    template_name = 'helpdesk/registration/login.html'
    
    def get_next_page(self):
        return self.request.GET.get('next', '/') 
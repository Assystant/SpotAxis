from django.views.generic import TemplateView

class RobotsTxtView(TemplateView):
    """
    View for serving robots.txt with proper content type.
    """
    template_name = 'robots.txt'
    content_type = 'text/plain'

class SitemapXmlView(TemplateView):
    """
    View for serving sitemap.xml with proper content type.
    """
    template_name = 'sitemap.xml'
    content_type = 'text/plain'

class GoogleVerificationView(TemplateView):
    """
    View for serving Google site verification file.
    """
    template_name = 'google7467b69f25fa8f1e.html' 
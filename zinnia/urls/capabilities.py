"""
URLs for the Zinnia capabilities endpoints.

These URLs expose various metadata files that inform clients,
browsers, or bots about the blog’s capabilities.

View Classes Used:
- RsdXml:           Really Simple Discovery (RSD) for remote editors
- WLWManifestXml:   Manifest for Windows Live Writer (WLW) integration
- OpenSearchXml:    OpenSearch description for browser search integration
- HumansTxt:        humans.txt for developer credits or meta info
"""

from django.conf.urls import url

from zinnia.views.capabilities import (
    HumansTxt,
    OpenSearchXml,
    RsdXml,
    WLWManifestXml
)

urlpatterns = [
    # --------------------------------------
    # RSD: Really Simple Discovery
    # Helps clients like WordPress detect APIs
    # Example: /rsd.xml
    # --------------------------------------
    url(r'^rsd.xml$', RsdXml.as_view(), name='rsd'),

    # --------------------------------------
    # humans.txt: Developer & team credits
    # Example: /humans.txt
    # --------------------------------------
    url(r'^humans.txt$', HumansTxt.as_view(), name='humans'),

    # --------------------------------------
    # OpenSearch: Browser search integration
    # Example: /opensearch.xml
    # --------------------------------------
    url(r'^opensearch.xml$', OpenSearchXml.as_view(), name='opensearch'),

    # --------------------------------------
    # WLW Manifest: For Windows Live Writer
    # Example: /wlwmanifest.xml
    # --------------------------------------
    url(r'^wlwmanifest.xml$', WLWManifestXml.as_view(), name='wlwmanifest'),
]

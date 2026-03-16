# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
import sys
# --- INÍCIO DO PATCH DE COMPATIBILIDADE ---
import django.utils.encoding
import django.utils.translation

# Redireciona funções antigas para as novas equivalentes do Django 4+
django.utils.encoding.smart_text = django.utils.encoding.smart_str
django.utils.encoding.force_text = django.utils.encoding.force_str
django.utils.translation.ugettext = django.utils.translation.gettext
django.utils.translation.ugettext_lazy = django.utils.translation.gettext_lazy
django.utils.translation.ugettext_noop = django.utils.translation.gettext_noop
# --- FIM DO PATCH DE COMPATIBILIDADE ---
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TRM.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

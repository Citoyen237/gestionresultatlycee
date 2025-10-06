from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _

# Register your models here.
admin.site.register(Classe)
admin.site.register(Matiere)
admin.site.register(Eleve)
admin.site.register(Enseignant)
admin.site.register(Evaluation)

admin.site.site_title = _("gestion des resultats")
admin.site.site_header = _("gestion des resultats")
admin.site.index_title = _("gestion des resultats")

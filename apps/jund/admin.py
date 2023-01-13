from django.contrib import admin
from .models import InscricaoEvento


@admin.register(InscricaoEvento)
class InscricaoEventoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'evento', 'email']


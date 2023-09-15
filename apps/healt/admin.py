from django.contrib import admin
from .models import (
    Paciente,
    Profissional,
    Evolucao
)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nome']


@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'especialidade']
    list_filter = ['especialidade']


@admin.register(Evolucao)
class EvolucaoAdmin(admin.ModelAdmin):
    list_display = ['plano']
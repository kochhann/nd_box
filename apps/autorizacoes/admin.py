from django.contrib import admin
from .models import (
    Autorizador,
    Aluno,
    Enturmacao,
    Coordenador,
    Evento,
    EventoUnidade,
    AutorizacoesModel,
    Autorizacao,
    EventoTipoAutorizacao
)


@admin.register(Coordenador)
class CoordenadorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'unidade', 'last_login', 'ativo']


@admin.register(Autorizador)
class AutorizadorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'last_login', 'ativo']


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'matricula', 'unidade', 'ativo']


@admin.register(Enturmacao)
class EnturmacaoAdmin(admin.ModelAdmin):
    list_display = ['unidade', 'aluno', 'turma', 'ativo']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'data_evento', 'scope', 'ativo']


@admin.register(EventoUnidade)
class EventoUnidadeAdmin(admin.ModelAdmin):
    list_display = ['evento', 'unidade', 'data_evento', 'ativo']


@admin.register(AutorizacoesModel)
class AutorizacoesModelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'gerador']


@admin.register(Autorizacao)
class AutorizacaoAdmin(admin.ModelAdmin):
    list_display = ['evento', 'aluno', 'autorizado', 'tipo', 'ativo']


@admin.register(EventoTipoAutorizacao)
class EventoTipoAutorizacaoAdmin(admin.ModelAdmin):
    list_display = ['tipo_autorizacao', 'evento', 'ativo']
    list_filter = ('evento', 'tipo_autorizacao',)

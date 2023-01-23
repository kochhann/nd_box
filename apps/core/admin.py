from django.contrib import admin
from apps.core.models import (
    Unidade,
    Curso,
    Ciclo,
    Turma
)


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cidade', 'cnpj', 'is_school', 'ativo']


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    ordering = ('unidade', 'nome')
    list_display = ['nome', 'unidade', 'gv_code', 'ativo']


@admin.register(Ciclo)
class CicloAdmin(admin.ModelAdmin):
    ordering = ('curso', 'nome')
    list_display = ['nome', 'unidade', 'curso', 'gv_code', 'ativo']
    list_filter = ['curso']

    def unidade(self, obj):
        return obj.curso.unidade.nome
    unidade.admin_order_field = 'unidade'  # set the field that is used for ordering
    unidade.short_description = 'Unidade'  # set the name of the column


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    ordering = ('nome', 'ciclo')
    list_display = ['nome', 'unidade', 'curso', 'ciclo', 'ano', 'ativo']
    list_filter = ['ano']

    def unidade(self, obj):
        return obj.ciclo.curso.unidade.nome
    unidade.admin_order_field = 'unidade'  # set the field that is used for ordering
    unidade.short_description = 'Unidade'  # set the name of the column

    def curso(self, obj):
        return obj.ciclo.curso.nome
    curso.short_description = 'Curso'  # set the name of the column

    def ciclo(self, obj):
        return obj.ciclo.nome
    ciclo.short_description = 'Ciclo'  # set the name of the column

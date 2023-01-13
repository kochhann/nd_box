from django.contrib import admin
from .models import (
    ScheduledTask,
    MailMessageScheduler,
    SmsCobrancaScheduler
)


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'status', 'error_message', 'extra_field', 'ativo']


@admin.register(MailMessageScheduler)
class MailMessageSchedulerAdmin(admin.ModelAdmin):
    list_display = ['unidade', 'assunto', 'enviado', 'data_envio']
    list_filter = ['enviado', 'unidade']


@admin.register(SmsCobrancaScheduler)
class SmsCobrancaSchedulerAdmin(admin.ModelAdmin):
    list_display = ['unidade', 'enviado', 'data_envio']
    list_filter = ['enviado', 'unidade']

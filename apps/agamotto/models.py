from django.db import models
from django.utils import timezone
from apps.core.models import (
    Base,
    Unidade
)
from hermes import (
    send_nd_mail,
    send_comtele
)


class ScheduledTask(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    task = models.CharField("Tarefa", max_length=100, blank=False, null=False)
    status = models.CharField("Status", max_length=100, blank=False, null=False)
    gv_code = models.IntegerField('GV Code', blank=True, null=True)
    extra_field = models.CharField("Extra", max_length=200, blank=True, null=True)
    error_message = models.CharField("Erro", max_length=500, blank=True, null=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.task + ' - ' + self.status


class MailMessageScheduler(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nd_code = models.IntegerField('Código ND', blank=True, null=True)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.SET_NULL, blank=True, null=True)
    codigo_aluno = models.IntegerField('Código ND do aluno', blank=True, null=True)
    data_geracao = models.DateField('Data de geração', blank=False, null=False)
    email_remetente = models.CharField("E-mail do remetente", max_length=200, blank=False, null=False)
    nome_remetente = models.CharField("Nome do remetente", max_length=200, blank=False, null=False)
    email_destino = models.CharField("E-mail de destino", max_length=200, blank=False, null=False)
    assunto = models.CharField("Assunto", max_length=200, blank=False, null=False)
    mensagem = models.TextField("Mensagem", blank=False, null=False)
    usuario = models.IntegerField('Usuário ND gerador', blank=True, null=True)
    data_envio = models.DateField('Data de envio', blank=True, null=True)
    enviado = models.BooleanField('Enviado', default=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def send(self):
        send_nd_mail(self)
        self.data_envio = timezone.now()
        self.enviado = True
        self.save()

    def __str__(self):
        return self.unidade.nome + ' - ' + self.assunto

    class Meta:
        verbose_name = 'E-mail Agendado'
        verbose_name_plural = 'E-mails Agendados'


class SmsCobrancaScheduler(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nd_code = models.IntegerField('Código ND', blank=True, null=True)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.SET_NULL, blank=True, null=True)
    codigo_aluno = models.IntegerField('Código ND do aluno', blank=True, null=True)
    data_geracao = models.DateField('Data de geração', blank=False, null=False)
    data_vencimento = models.DateField('Data de vencimento', blank=False, null=False)
    data_envio = models.DateField('Data de envio', blank=True, null=True)
    fone_destino = models.CharField("Telefone de destino", max_length=200, blank=False, null=False)
    mensagem = models.TextField("Mensagem", blank=False, null=False)
    enviado = models.BooleanField('Enviado', default=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def send(self):
        send_comtele('01', self.fone_destino, self.mensagem)
        self.data_envio = timezone.now()
        self.enviado = True
        self.save()

    def __str__(self):
        return self.unidade.nome + ' - ' + f'{self.codigo_aluno}'

    class Meta:
        verbose_name = 'SMS Agendado'
        verbose_name_plural = 'SMS Agendados'

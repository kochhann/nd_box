from django.db import models
from apps.core.models import Base
from apps.autorizacoes.models import Evento
from django.utils import timezone
from datetime import date
from django.urls import reverse
from functions import calculate_age


class InscricaoEvento(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    id_jund = models.IntegerField('ID Jund', blank=True, null=True)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)
    email = models.EmailField('E-mail', max_length=200, blank=False, null=False, default='Não informado')
    cidade = models.CharField('Cidade', max_length=200, blank=True, null=True, default='Canoas')
    telefone = models.CharField('Telefone', max_length=15, blank=True, null=True)
    data_nascimento = models.DateField('Data de Nascimento', blank=True, null=True)
    id_grupo = models.IntegerField('Grupo', blank=True, null=True)
    confirmada = models.BooleanField("Confirmada", blank=True, null=True, default=None)
    evento = models.ForeignKey(Evento, verbose_name='Evento', on_delete=models.CASCADE, blank=False, null=False)
    nome_responsavel = models.CharField('Nome Responsável', max_length=200, blank=False, null=False)
    email_responsavel = models.EmailField('E-mail Responsável', max_length=200, blank=False, null=False)
    cpf_responsavel = models.CharField('CPF Responsável', max_length=20, blank=False, null=False)
    restricoes = models.CharField('E-mail Responsável', max_length=500, blank=True, null=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.nome

    @property
    def is_past_due(self):
        return date.today() > self.data_criacao

    @property
    def age(self):
        return calculate_age(self.data_nascimento)

    @staticmethod
    def get_absolute_url():
        return reverse('index')

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'

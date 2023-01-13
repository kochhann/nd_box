from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.core.models import Unidade, Base
from functions import get_file_path
from datetime import date, timedelta


class Area(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Área de Interesse'
        verbose_name_plural = 'Áreas de Interesse'


class Escolaridade(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Escolaridade'
        verbose_name_plural = 'Escolaridades'


class Vaga(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.SET_NULL, blank=True, null=True)
    cod_vaga = models.CharField('Código', max_length=200, blank=True, null=True)
    area_interesse = models.ForeignKey(Area, verbose_name='Área de interesse', on_delete=models.SET_NULL, blank=True,
                                       null=True)
    titulo = models.CharField('Título', max_length=200, blank=False, null=False)
    descricao = models.TextField('Descrição', max_length=1000, blank=False, null=False)
    escolaridade = models.ForeignKey(Escolaridade, verbose_name='Escolaridade', on_delete=models.SET_NULL, blank=True,
                                     null=True)
    tempo_experiencia = models.CharField('Tempo de experiência', max_length=200, blank=True, null=True)
    aberta = models.BooleanField('Aberta', default=True)
    preenchida = models.BooleanField('Preenchida', default=False)
    msg_erro_exclusao = models.CharField("Mens. Erro exclusão", max_length=400, blank=True, null=True)
    data_fechamento = models.DateField('Data Fechamento', blank=True, null=True)
    data_preenchida = models.DateField('Data Preenchimento', blank=True, null=True)

    @staticmethod
    def get_absolute_url():
        return reverse('index')

    @property
    def nbr_applications(self):
        return len(self.candidatura_set.all())

    def soft_delete(self):
        candidaturas = self.candidatura_set.all()
        if candidaturas:
            self.msg_erro_exclusao = 'Não é possível excluir esta vaga, pois existem candidaturas' \
                                     ' ativas. Ao invés ' \
                                     'disso, tente fechar'
            self.save()
            return False
        else:
            self.ativo = False
            self.data_desativado = timezone.now()
            self.save()
            return True

    def close(self):
        self.data_fechamento = timezone.now()
        self.aberta = False
        self.save()

    def fill(self):
        self.data_preenchida = timezone.now()
        self.preenchida = True
        self.close()

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Vaga'
        verbose_name_plural = 'Vagas'


class Candidatura(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    cod_vaga = models.ForeignKey(Vaga, verbose_name='Vaga', on_delete=models.SET_NULL, blank=True, null=True)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)
    email = models.CharField('E-mail', max_length=200, blank=False, null=False)
    cidade = models.CharField('Cidade', max_length=200, blank=True, null=True, default='Canoas')
    telefone = models.CharField('Telefone', max_length=15, blank=False, null=False)
    escolaridade = models.ForeignKey(Escolaridade, verbose_name='Escolaridade', on_delete=models.SET_NULL, blank=True,
                                     null=True)
    curso = models.CharField('Curso', max_length=100, blank=True, null=True)
    historico = models.TextField('Pós-graduação', max_length=300, blank=True, null=True)
    area_interesse = models.ForeignKey(Area, on_delete=models.SET_NULL, verbose_name='Área de interesse', blank=True,
                                       null=True, default=None)
    unidade_interesse = models.ForeignKey(Unidade, on_delete=models.SET_NULL, verbose_name='Unidade de interesse',
                                          blank=True, null=True, default=None)
    tempo_experiencia = models.CharField('', max_length=100, blank=True, null=True)
    arquivo = models.FileField(upload_to=get_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return str(self.cod_vaga) + ' - ' + str(self.nome)

    @property
    def expire_date(self):
        return self.data_criacao + timedelta(days=365)

    @property
    def is_past_due(self):
        return date.today() > self.data_criacao

    class Meta:
        verbose_name = 'Candidatura'
        verbose_name_plural = 'Candidaturas'

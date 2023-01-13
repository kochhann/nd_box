from django.db import models
from django.utils import timezone


class Base(models.Model):
    data_criacao = models.DateField('Criação', auto_now_add=True)
    data_modificacao = models.DateField('Modificação', auto_now=True)
    data_desativado = models.DateField('Desativado', blank=True, null=True, default=None)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        abstract = True


class Unidade(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)
    cidade = models.CharField('Cidade', max_length=200, blank=False, null=False)
    estado = models.CharField('Estado', max_length=2, blank=False, null=False)
    is_school = models.BooleanField('É escola', default=False)
    cnae = models.CharField('CNAE', max_length=20, blank=True, null=True)
    cnpj = models.CharField('CNPJ', max_length=20, blank=True, null=True)
    gv_code = models.IntegerField('GV Code', blank=False, null=False, unique=True)

    def update_from_origin(self, gv_origin):
        self.nome = gv_origin.nome.title()
        self.cidade = gv_origin.cidade.title()
        self.estado = gv_origin.estado
        self.cnae = gv_origin.cnae
        self.cnpj = gv_origin.cnpj
        self.save()

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'


class Curso(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)
    gv_code = models.IntegerField('GV Code', blank=False, null=False, unique=True)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.SET_NULL, blank=True, null=True)

    def update_from_origin(self, gv_origin):
        self.nome = gv_origin.nome.title()
        self.save()

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    @property
    def get_unidade(self):
        return self.unidade

    def __str__(self):
        return str(self.unidade.gv_code) + ' - ' + self.nome

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'


class Ciclo(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)
    gv_code = models.IntegerField('GV Code', blank=False, null=False, unique=True)
    curso = models.ForeignKey(Curso, verbose_name='Curso', on_delete=models.SET_NULL, blank=True, null=True)

    def update_from_origin(self, gv_origin):
        self.nome = gv_origin.nome.title()
        self.save()

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    @property
    def get_curso(self):
        return self.curso

    @property
    def get_unidade(self):
        return self.curso.get_unidade

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Ciclo'
        verbose_name_plural = 'Ciclos'


class Turma(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)
    ano = models.IntegerField('Ano', blank=False, null=False)
    ciclo = models.ForeignKey(Ciclo, verbose_name='Ciclo', on_delete=models.SET_NULL, blank=True, null=True)
    gv_code = models.IntegerField('GV Code', blank=False, null=False, unique=True)

    def update_from_origin(self, gv_origin):
        self.nome = gv_origin.nome.title()
        self.ano = gv_origin.ano
        self.save()

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    @property
    def get_ciclo(self):
        return self.ciclo

    @property
    def get_curso(self):
        return self.ciclo.get_curso

    @property
    def get_unidade(self):
        return self.ciclo.get_unidade

    @property
    def is_past_due(self):
        return timezone.now().year > self.ano

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'

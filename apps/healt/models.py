from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta


def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    return age


class Base(models.Model):
    data_criacao = models.DateTimeField('Criação', auto_now_add=True)
    data_desativado = models.DateField('Desativado', blank=True, null=True, default=None)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        abstract = True


class Profissional(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nd_code = models.IntegerField(unique=True, blank=False, null=False)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)
    id_funcional = models.CharField('Funcional', max_length=200, blank=True, null=True)
    especialidade = models.CharField('Especialidade', max_length=200, blank=True, null=True)
    contato = models.CharField('Contato', max_length=200, blank=True, null=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'


class Paciente(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nd_code = models.IntegerField(unique=True, blank=False, null=False)
    nome = models.CharField('Nome', max_length=200, blank=False, null=False)
    data_nascimento = models.DateField('Nascimento', blank=True, null=True)
    data_falecimento = models.DateField('Falecimento', blank=True, null=True)
    nome_pai = models.CharField('Pai', max_length=200, blank=True, null=True)
    nome_mae = models.CharField('Mãe', max_length=200, blank=True, null=True)
    contato = models.CharField('Contato', max_length=200, blank=False, null=False)
    falecido = models.BooleanField('Falecido', default=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def get_age(self):
        if self.data_nascimento is not None:
            #format(minha_data, "%d/%m/%Y")
            return (f'{calculate_age(self.data_nascimento)} anos'
                    f' ({self.data_nascimento:%d/%m/%Y})')
        return 'Data de nascimento não informada.'

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'


class Evolucao(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    profissional = models.ForeignKey(Profissional, verbose_name='Profissional', on_delete=models.PROTECT,
                                     blank=False, null=False)
    paciente = models.ForeignKey(Paciente, verbose_name='Paciente', on_delete=models.PROTECT, blank=False, null=False)
    subjetivo = models.CharField('Subjetivo', max_length=500, blank=False, null=False)
    objetivo = models.CharField('Objetivo', max_length=500, blank=False, null=False)
    avaliacao = models.CharField('Avaliação', max_length=500, blank=False, null=False)
    plano = models.CharField('Plano', max_length=500, blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.paciente.nome + ' - ' + self.profissional.especialidade

    class Meta:
        verbose_name = 'Evolução'
        verbose_name_plural = 'Evoluções'


class Afericoes(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    profissional = models.ForeignKey(Profissional, verbose_name='Profissional', on_delete=models.PROTECT,
                                     blank=False, null=False)
    paciente = models.ForeignKey(Paciente, verbose_name='Paciente', on_delete=models.PROTECT, blank=False, null=False)
    temperatura = models.DecimalField('Temperatura', max_digits=6, decimal_places=2, blank=True, null=True)
    sistolica = models.DecimalField('Sistólica', max_digits=6, decimal_places=2, blank=True, null=True)
    diastolica = models.DecimalField('Diastólica', max_digits=6, decimal_places=2, blank=True, null=True)
    media = models.DecimalField('PA Média', max_digits=6, decimal_places=2, blank=True, null=True)
    freq_respiratoria = models.DecimalField('Freq. Respiratória', max_digits=6, decimal_places=2, blank=True, null=True)
    freq_cardiaca = models.DecimalField('Freq. Cardíaca', max_digits=6, decimal_places=2, blank=True, null=True)
    pulso = models.DecimalField('Pulso', max_digits=6, decimal_places=2, blank=True, null=True)
    glicemia = models.DecimalField('Glicemia', max_digits=6, decimal_places=2, blank=True, null=True)
    coleta = models.DecimalField('Coleta', max_digits=6, decimal_places=2, blank=True, null=True)
    saturacao_o2 = models.DecimalField('Saturação O2', max_digits=6, decimal_places=2, blank=True, null=True)
    saturacao_co2 = models.DecimalField('Saturação CO2', max_digits=6, decimal_places=2, blank=True, null=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def pressao_arterial(self):
        return f'{self.sistolica}/{self.diastolica}'

    def __str__(self):
        return self.paciente.nome

    class Meta:
        verbose_name = 'Aferição'
        verbose_name_plural = 'Aferições'


class Medidas(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    profissional = models.ForeignKey(Profissional, verbose_name='Profissional', on_delete=models.PROTECT,
                                     blank=False, null=False)
    paciente = models.ForeignKey(Paciente, verbose_name='Paciente', on_delete=models.PROTECT, blank=False, null=False)
    superficie_corporal = models.DecimalField('Superf. corporal', max_digits=6, decimal_places=2, blank=True, null=True)
    quadril = models.DecimalField('Quadril', max_digits=6, decimal_places=2, blank=True, null=True)
    cintura = models.DecimalField('Cintura', max_digits=6, decimal_places=2, blank=True, null=True)
    circulacao_braquial = models.DecimalField('Circ. braquial', max_digits=6, decimal_places=2, blank=True, null=True)
    pg_cutaneas = models.DecimalField('Pregas cutâneas', max_digits=6, decimal_places=2, blank=True, null=True)
    estado_nutricional = models.CharField('Est. nutricional',max_length=1000, blank=True, null=True)
    panturrilha = models.DecimalField('Panturrilha', max_digits=6, decimal_places=2, blank=True, null=True)
    altura = models.DecimalField('Altura', max_digits=6, decimal_places=2, blank=True, null=True)
    peso = models.DecimalField('Peso', max_digits=6, decimal_places=2, blank=True, null=True)
    imc = models.DecimalField('IMC', max_digits=6, decimal_places=2, blank=True, null=True)
    observacao = models.CharField('Observação', max_length=1500, blank=True, null=True)
    dieta = models.CharField('Dieta', max_length=1000, blank=True, null=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.paciente.nome

    class Meta:
        verbose_name = 'Medidas'
        verbose_name_plural = 'Medidas'


class Cuidados(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    profissional = models.ForeignKey(Profissional, verbose_name='Profissional', on_delete=models.PROTECT,
                                     blank=False, null=False)
    paciente = models.ForeignKey(Paciente, verbose_name='Paciente', on_delete=models.PROTECT, blank=False, null=False)
    cuidado = models.CharField('Cuidado', max_length=500, blank=False, null=False)
    observacao = models.CharField('Observação', max_length=500, blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.paciente.nome

    class Meta:
        verbose_name = 'Cuidado'
        verbose_name_plural = 'Cuidados'


class Prescricao(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    profissional = models.ForeignKey(Profissional, verbose_name='Profissional', on_delete=models.PROTECT,
                                     blank=False, null=False)
    paciente = models.ForeignKey(Paciente, verbose_name='Paciente', on_delete=models.PROTECT, blank=False, null=False)
    farmaco = models.CharField('Fármaco', max_length=500, blank=True, null=True)
    aplicacao = models.CharField('Aplicação', max_length=500, blank=True, null=True)
    data_inicio = models.DateField('Início', blank=True, null=True)
    data_fim = models.DateField('Fim', blank=True, null=True)
    motivo = models.CharField('Motivo', max_length=500, blank=True, null=True)
    intervalo = models.CharField('Intervalo', max_length=500, blank=True, null=True)
    horario = models.CharField('Horário', max_length=500, blank=True, null=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.paciente.nome

    class Meta:
        verbose_name = 'Prescrição'
        verbose_name_plural = 'Prescrições'


class Vacinacao(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    paciente = models.ForeignKey(Paciente, verbose_name='Paciente', on_delete=models.PROTECT, blank=False, null=False)
    profissional = models.CharField('Profissional', max_length=100, blank=True, null=True)
    vacina = models.CharField('Vacina', max_length=100, blank=False, null=False)
    lote = models.CharField('Lote', max_length=100, blank=False, null=False)
    id_carteira = models.CharField('Carteira de vacinação', max_length=100, blank=False, null=False)
    localidade = models.CharField('Localidade', max_length=100, blank=False, null=False)
    data = models.DateField('Data aplicação', blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.paciente.nome

    class Meta:
        verbose_name = 'Vacinação'
        verbose_name_plural = 'Vacinações'

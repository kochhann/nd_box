from django.db import models
import uuid
from django.urls import reverse
from datetime import date, timedelta
from hermes import (
    send_cancel_mail,
    send_new_notification_mail
)
from apps.core.models import (
    Base,
    Turma,
    Ciclo,
    Curso,
    Unidade
)
from apps.agamotto.models import ScheduledTask
from django.utils import timezone
from django.contrib.auth.models import User


def get_file_path(_instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return filename


class Autorizador(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    user = models.ForeignKey(User, verbose_name='Usuário', on_delete=models.PROTECT, blank=False, null=False)
    gv_code = models.IntegerField('GV Code', blank=False, null=False, unique=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def send_login_mail(self):
        return self.user.name

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    @property
    def last_login(self):
        return self.user.last_login

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

    class Meta:
        verbose_name = 'Autorizador'
        verbose_name_plural = 'Autorizadores'


class Coordenador(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.PROTECT, blank=False,
                                null=False)
    user = models.ForeignKey(User, verbose_name='Usuário', on_delete=models.PROTECT, blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    @property
    def last_login(self):
        return self.user.last_login

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

    class Meta:
        verbose_name = 'Coordenador'
        verbose_name_plural = 'Coordenadores'


class Aluno(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField("Nome", max_length=100, blank=False, null=False)
    matricula = models.IntegerField("Matrícula", blank=False, null=False, unique=True)
    gv_code = models.IntegerField('GV Code', blank=False, null=False, unique=True)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.PROTECT, blank=False,
                                null=False)
    responsavel = models.ForeignKey(Autorizador, verbose_name='Autorizador', on_delete=models.PROTECT, blank=False,
                                    null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def update_enturmacao(self, gv_origin):
        self.remove_enturmacao()
        self.create_enturmacao(Turma.objects.get(gv_code=gv_origin))
        print('alteração de turma concluída!')
        # gerenciar autorizações
        aut = self.autorizacao_set.filter(ativo=True, cancelado=False)
        autorizacoes = []
        for i in aut:
            if not i.evento.is_past_due:
                autorizacoes.append(i)

        if autorizacoes:  # há autorizações para eventos futuros
            for i in autorizacoes:
                if i.evento.turma is not None:
                    i.cancelar('Aluno trocou de turma.')
        # Verificar eventos da nova turma
        eventos = Evento.objects.filter(ativo=True)
        aut = self.autorizacao_set.filter(ativo=True, cancelado=False)
        eventos_aluno = []
        for i in aut:
            eventos_aluno.append(i.evento)

        for e in eventos:
            aut = e.autorizacao_set.filter(ativo=True, aluno=self)
            if not aut:
                if e.unidade == self.unidade:
                    eventos_aluno.append(e)
                if e.aluno == self:
                    eventos_aluno.append(e)
                if e.turma == self.turma_atual:
                    eventos_aluno.append(e)
                if e.ciclo == self.turma_atual.get_ciclo:
                    eventos_aluno.append(e)
                if e.curso == self.turma_atual.get_curso:
                    eventos_aluno.append(e)
        eventos_aluno = list(dict.fromkeys(eventos_aluno))
        if eventos_aluno:
            for e in eventos_aluno:
                e.gera_aut_aluno(self)
        print('gestão de autorizações concluída!')

    def create_enturmacao(self, turma):
        enturmacao = Enturmacao(unidade=self.unidade,
                                aluno=self,
                                turma=turma)
        enturmacao.save()

    def remove_enturmacao(self):
        ent = self.enturmacao_set.get(ativo=True)
        ent.soft_delete()

    @property
    def turma_atual(self):
        tur = self.enturmacao_set.get(ativo=True).turma
        return tur

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


class Enturmacao(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.PROTECT, blank=False, null=False)
    aluno = models.ForeignKey(Aluno, verbose_name='Aluno', on_delete=models.PROTECT, blank=False, null=False)
    turma = models.ForeignKey(Turma, verbose_name='Turma', on_delete=models.PROTECT, blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.aluno.nome + ' ' + self.turma.nome + ' - ' + str(self.turma.ano)

    @property
    def is_past_due(self):
        return timezone.now().year > self.turma.ano

    class Meta:
        verbose_name = 'Enturmação'
        verbose_name_plural = 'Enturmações'


class Evento(Base):
    GERADOR_CHOICES = [
        (1, 'Instituição'),
        (2, 'Família'),
        (3, 'JUND'),
    ]

    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField("Nome", max_length=200, blank=False, null=False)
    descricao = models.CharField("Descricao", max_length=1000, blank=False, null=False)
    data_evento = models.DateField('Data', blank=False, null=False)
    gerador = models.IntegerField("Gerador", choices=GERADOR_CHOICES, blank=False, null=False, default=1)
    data_termino = models.DateField('Data Término', blank=False, null=False)
    data_cancelamento = models.DateField('Data Cancelamento', blank=True, null=True)
    local_evento = models.CharField("Cidade/UF", max_length=100, blank=False, null=False)
    aluno = models.ForeignKey(Aluno, verbose_name='Aluno', on_delete=models.SET_NULL, blank=True, null=True)
    turma = models.ForeignKey(Turma, verbose_name='Turma', on_delete=models.SET_NULL, blank=True, null=True)
    ciclo = models.ForeignKey(Ciclo, verbose_name='Ciclo', on_delete=models.SET_NULL, blank=True, null=True)
    curso = models.ForeignKey(Curso, verbose_name='Curso', on_delete=models.SET_NULL, blank=True, null=True)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.SET_NULL, blank=True, null=True)
    obs_cancelamento = models.CharField("Obs. Cancelamento", max_length=400, blank=True, null=True)
    msg_erro_cancelamento = models.CharField("Mens. Erro Cancelamento", max_length=400, blank=True, null=True)

    def gera_autorizacoes(self, tipo):
        alunos = []
        model = AutorizacoesModel.objects.get(pk=tipo)
        if self.aluno is not None:
            alunos.append(self.aluno)

        if self.turma is not None:
            ent = Enturmacao.objects.filter(turma=self.turma)
            for item in ent:
                alunos.append(item.aluno)

        if self.ciclo is not None:
            ciclo = Ciclo.objects.get(pk=self.ciclo.pk)
            for item in ciclo.turma_set.all():
                for ent in item.enturmacao_set.all():
                    alunos.append(ent.aluno)

        if self.curso is not None:
            curso = Curso.objects.get(pk=self.curso.pk)
            for ciclo in curso.ciclo_set.all():
                for turma in ciclo.turma_set.all():
                    for ent in turma.enturmacao_set.all():
                        alunos.append(ent.aluno)

        if self.unidade is not None:
            unidade = Unidade.objects.get(pk=self.unidade.pk)
            for curso in unidade.curso_set.all():
                for ciclo in curso.ciclo_set.all():
                    for turma in ciclo.turma_set.all():
                        for ent in turma.enturmacao_set.all():
                            alunos.append(ent.aluno)

        autorizacoes_geradas = self.autorizacao_set.filter(tipo=model)
        alunos_processados = []
        for a in autorizacoes_geradas:
            alunos_processados.append(a.aluno)
        lista_nova = set(alunos_processados) ^ set(alunos)
        if len(lista_nova) > 0:
            for aluno in lista_nova:
                aut = Autorizacao(evento=self,
                                  responsavel=aluno.responsavel,
                                  tipo=model,
                                  aluno=aluno,
                                  termos=model.texto)
                aut.save()
                send_new_notification_mail(self, aluno.responsavel)

    def gera_aut_aluno(self, aluno):
        tipo_aut = self.eventotipoautorizacao_set.filter(ativo=True)
        for tipo in tipo_aut:
            aut = Autorizacao(evento=self,
                              responsavel=aluno.responsavel,
                              tipo=tipo.tipo_autorizacao,
                              aluno=aluno,
                              termos=tipo.tipo_autorizacao.texto)
            aut.save()

    def soft_delete(self):
        autorizacoes = self.autorizacao_set.all()
        st = ScheduledTask.objects.filter(task='generateAuth', ativo=True, gv_code=self.pk)
        if autorizacoes:
            self.msg_erro_cancelamento = 'Não é possível excluir o evento, pois existem autorizações geradas. Ao' \
                                         ' invés disso, tente cancelar'
            self.save()
            return False
        if st:
            for i in st:
                i.status = 'canceled'
                i.soft_delete()

        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()
        return True

    def cancelar(self, motivo):
        self.data_cancelamento = timezone.now()
        self.obs_cancelamento = motivo
        self.save()
        autorizacoes = self.autorizacao_set.all()
        responsaveis = []
        for aut in autorizacoes:
            responsaveis.append(aut.responsavel)
            aut.cancelar('Evento cancelado.')
        responsaveis = list(dict.fromkeys(responsaveis))
        for item in responsaveis:
            send_cancel_mail(self, item)

    def __str__(self):
        return self.nome

    @staticmethod
    def get_absolute_url():
        return reverse('index')

    @property
    def scope(self):
        if self.aluno is not None:
            return self.aluno.nome
        if self.turma is not None:
            return 'Turma ' + self.turma.nome
        if self.ciclo is not None:
            return self.ciclo.nome
        if self.curso is not None:
            return self.curso.nome
        if self.unidade is not None:
            return self.unidade.nome

    @property
    def is_past_due(self):
        return date.today() > self.data_evento

    @property
    def is_canceled(self):
        return self.data_cancelamento is not None

    @property
    def has_documents(self):
        return len(self.autorizacao_set.all()) > 0

    @property
    def has_scheduled_docs(self):
        st = ScheduledTask.objects.filter(task='generateAuth', ativo=True, gv_code=self.pk).exclude(status='canceled')
        return len(st) > 0

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'


class EventoUnidade(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    evento = models.ForeignKey(Evento, verbose_name='Evento', on_delete=models.CASCADE, blank=False, null=False)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.CASCADE, blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.evento.nome

    @property
    def data_evento(self):
        return self.evento.data_evento


class AutorizacoesModel(Base):
    GERADOR_CHOICES = [
        (1, 'Instituição'),
        (2, 'Família'),
    ]

    id = models.AutoField(primary_key=True, blank=False, null=False)
    nome = models.CharField("Nome", max_length=100, blank=False, null=False)
    texto = models.TextField("Texto", blank=False, null=False)
    apelido = models.CharField("Apelido", max_length=15, blank=False, null=False)
    gerador = models.IntegerField("Gerador", choices=GERADOR_CHOICES, blank=False, null=False, default=1)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Tipo de Autorização'
        verbose_name_plural = 'Tipos de Autorização'


class Autorizacao(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    evento = models.ForeignKey(Evento, verbose_name='Evento', on_delete=models.PROTECT, blank=True, null=True)
    responsavel = models.ForeignKey(Autorizador, verbose_name='Responsável', on_delete=models.PROTECT, blank=False,
                                    null=False)
    tipo = models.ForeignKey(AutorizacoesModel, verbose_name='Tipo', on_delete=models.PROTECT, blank=False, null=False)
    aluno = models.ForeignKey(Aluno, verbose_name='Aluno', on_delete=models.PROTECT, blank=False, null=False)
    termos = models.TextField("Termos", blank=False, null=False)
    autorizado = models.BooleanField("Autorização", blank=True, null=True, default=None)
    data_resposta_titular = models.DateField('Data Resposta', blank=True, null=True)
    cancelado = models.BooleanField("Cancelado", blank=False, null=False, default=False)
    data_cancelamento = models.DateField('Data Cancelamento', blank=True, null=True)
    obs_cancelamento = models.CharField("Obs. Cancelamento", max_length=400, blank=True, null=True)
    revogado = models.BooleanField("Revogado", blank=False, null=False, default=False)
    data_revogacao = models.DateField('Data Revogação', blank=True, null=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.evento.nome

    def autorizar(self):
        self.autorizado = True
        self.revogado = False
        self.data_revogacao = None
        self.data_resposta_titular = timezone.now()
        self.save()

    def recusar(self):
        self.autorizado = False
        self.data_resposta_titular = timezone.now()
        self.save()

    def cancelar(self, motivo):
        self.cancelado = True
        self.data_cancelamento = timezone.now()
        self.obs_cancelamento = motivo
        self.save()

    def revogar(self):
        self.revogado = True
        self.data_revogacao = timezone.now()
        self.save()

    @property
    def expire_date(self):
        return self.evento.data_evento + timedelta(days=365)

    @property
    def is_about_expire(self):
        today = timezone.now().date()
        return (self.expire_date - today) < timedelta(days=10)

    @staticmethod
    def get_absolute_url():
        return reverse('index')

    class Meta:
        verbose_name = 'Autorização'
        verbose_name_plural = 'Autorizações'


class AnexoAutorizacao(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    descricao = models.CharField('Descrição', max_length=100, blank=False, null=False, default='anexo')
    arquivo = models.FileField(upload_to=get_file_path, blank=True, null=True)
    numero = models.IntegerField('Número de sequência', blank=True, null=True, default=1)
    autorizacao = models.ForeignKey(Autorizacao, verbose_name='Autorização', on_delete=models.SET_NULL, blank=True,
                                    null=True)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return str(self.numero) + ' - ' + self.autorizacao.aluno.nome

    class Meta:
        verbose_name = 'Anexo de autorização'
        verbose_name_plural = 'Anexos de Autorização'


class EventoTipoAutorizacao(Base):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    tipo_autorizacao = models.ForeignKey(AutorizacoesModel,
                                         verbose_name='Tipo de Autorização',
                                         related_name='tipos_autorizacao',
                                         on_delete=models.CASCADE,
                                         blank=False, null=False)
    evento = models.ForeignKey(Evento, verbose_name='Evento',
                               on_delete=models.CASCADE,
                               blank=False, null=False)

    def soft_delete(self):
        self.ativo = False
        self.data_desativado = timezone.now()
        self.save()

    def __str__(self):
        return self.evento.nome + ' - ' + self.tipo_autorizacao.nome

    class Meta:
        verbose_name = 'Tipo de Autorização do Evento'
        verbose_name_plural = 'Tipos de Autorização do Evento'

from django.contrib import messages
from operator import attrgetter
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from io import BytesIO

from django.utils.decorators import method_decorator
from reportlab.lib.colors import black
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus import (
    Table,
    TableStyle
)
from apps.reports.printing import *
from django.views.generic import (
    View,
    TemplateView,
    DeleteView,
    CreateView,
    ListView,
    UpdateView,
    DetailView,
    FormView
)
from .models import (
    Autorizador,
    Evento,
    EventoUnidade,
    Coordenador,
    Aluno,
    Autorizacao,
    AutorizacoesModel,
    EventoTipoAutorizacao
)
from apps.core.models import (
    Turma,
    Ciclo,
    Curso,
    Unidade
)
from .forms import (
    EventoForm,
    EventoEditForm,
    EventoCancelForm,
    AutorizacaoForm
)
from apps.agamotto.models import ScheduledTask


@method_decorator(login_required, name='dispatch')
class AutorizadorView(TemplateView):
    template_name = 'autorizador_index.html'

    def get_context_data(self, **kwargs):
        context = super(AutorizadorView, self).get_context_data(**kwargs)
        aut = Autorizador.objects.get(user=self.request.user)
        context['doc_title'] = 'Área do Usuário'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Área do usuário'
        context['pt_span'] = 'Detalhes da sua conta'
        context['pt_breadcrumb2'] = 'Área do usuário'
        context['autorizador'] = aut
        context['dependentes'] = aut.aluno_set.all()

        return context


class EventoDelete(DeleteView):
    model = Evento
    success_url = reverse_lazy('index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.soft_delete():
            ev_un = EventoUnidade.objects.get(evento=self.object.pk)
            ev_un.soft_delete()
            messages.success(self.request, 'Evento excluído com sucesso!')
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.success(self.request, self.object.msg_erro_cancelamento)
            url = reverse('evento-detail', kwargs={'pk': self.object.pk})
            return HttpResponseRedirect(url)


class EventoCreate(CreateView):
    model = Evento
    form_class = EventoForm

    def get_context_data(self, **kwargs):
        coord = Coordenador.objects.get(user=self.request.user)
        unidade = coord.unidade
        t_autorizacoes = AutorizacoesModel.objects.filter(ativo=True, gerador=1)
        cursos = Curso.objects.filter(unidade=unidade, ativo=True)
        alunos = Aluno.objects.filter(unidade=unidade, ativo=True)
        ciclos = Ciclo.objects.filter(curso__in=cursos, ativo=True)
        turmas = Turma.objects.filter(ciclo__in=ciclos, ativo=True)
        unidades = Unidade.objects.filter(pk=coord.unidade.pk)
        context = super(EventoCreate, self).get_context_data(**kwargs)
        context['coordenador'] = coord
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        context['turmas'] = turmas
        context['ciclos'] = ciclos
        context['cursos'] = cursos
        context['alunos'] = alunos
        context['unidades'] = unidades
        context['t_autorizacoes'] = t_autorizacoes
        return context

    def form_valid(self, form, *args, **kwargs):
        evento = form.save(commit=False)
        evento.ativo = True
        evento.gerador = 1
        evento.save()
        tipo = form.cleaned_data.get('tipo_autorizacao')
        # inclui as categorias de autorização que serão necessárias
        for i in tipo:
            ta = AutorizacoesModel.objects.get(pk=i.pk)
            tipos_evento = EventoTipoAutorizacao(tipo_autorizacao=ta,
                                                 evento=evento)
            tipos_evento.save()

        coord = Coordenador.objects.get(user=self.request.user)
        ev_un = EventoUnidade(evento=evento, unidade=coord.unidade)
        ev_un.save()
        messages.success(self.request, 'Evento ' + evento.nome + ' criado com sucesso')
        return super(EventoCreate, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        print(form.errors)
        return super(EventoCreate, self).form_invalid(form, *args, **kwargs)


class EventoUnidadeList(ListView):
    model = EventoUnidade
    template_name = 'coordenador_evento_list.html'

    def get_context_data(self, **kwargs):
        coord = Coordenador.objects.get(user=self.request.user)
        context = super(EventoUnidadeList, self).get_context_data(**kwargs)
        ev_un = EventoUnidade.objects.filter(ativo=True, unidade=coord.unidade, evento__gerador=1)
        eventos = sorted(ev_un, key=attrgetter('evento.data_evento'))
        passados = []
        agendados = []
        cancelados = []
        for e in eventos:
            if e.evento.is_canceled:
                cancelados.append(e)
            elif e.evento.is_past_due:
                passados.append(e)
            else:
                agendados.append(e)
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        context['eventos'] = eventos
        context['passados'] = passados
        context['agendados'] = agendados
        context['cancelados'] = cancelados
        return context


class EventoEdit(UpdateView):
    model = Evento
    form_class = EventoEditForm
    template_name = 'autorizacoes/evento_edit_form.html'

    def get_context_data(self, **kwargs):
        coord = Coordenador.objects.get(user=self.request.user)
        context = super(EventoEdit, self).get_context_data(**kwargs)
        t_autorizacoes = AutorizacoesModel.objects.all()
        t_aut_evento = self.object.eventotipoautorizacao_set.all()
        t_autorizacoes_ev = []
        if t_aut_evento:
            for e in t_aut_evento:
                t_autorizacoes_ev.append(e.tipo_autorizacao)
            autor_disponiveis = set(t_autorizacoes) ^ set(t_autorizacoes_ev)

        autorizacoes = self.object.autorizacao_set.all()
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        context['coordenador'] = coord
        context['t_autorizacoes'] = t_aut_evento
        context['autorizacoes_disponiveis'] = autor_disponiveis
        context['autorizacoes_geradas'] = autorizacoes

        return context

    def form_valid(self, form):
        evento = form.save()
        tipo = form.cleaned_data.get('tipo_autorizacao')
        if tipo:
            for i in tipo:
                ta = AutorizacoesModel.objects.get(pk=i.pk)
                tipos_evento = EventoTipoAutorizacao(tipo_autorizacao=ta,
                                                     evento=evento)
                tipos_evento.save()

        messages.success(self.request, 'Evento ' + evento.nome + ' alterado com sucesso')
        return super(EventoEdit, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, 'Erro no preenchimento: ' + str(form.errors))
        return super(EventoEdit, self).form_invalid(form, *args, **kwargs)


class EventoCancel(UpdateView):
    model = Evento
    form_class = EventoCancelForm
    template_name = 'autorizacoes/evento_cancel_form.html'

    def get_context_data(self, **kwargs):
        context = super(EventoCancel, self).get_context_data(**kwargs)
        coord = Coordenador.objects.get(user=self.request.user)
        aut = self.object.autorizacao_set.all()
        t_aut = self.object.eventotipoautorizacao_set.all()
        geradas = len(aut)
        aceitas = 0
        negadas = 0
        for a in aut:
            if a.autorizado == 'Autorizado':
                aceitas += 1
            else:
                negadas += 1
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        context['t_autorizacoes'] = t_aut
        context['autorizacoes'] = geradas
        context['aceitas'] = aceitas
        context['negadas'] = negadas
        return context

    def form_valid(self, form):
        evento = form.save(commit=False)
        evento.cancelar(evento.obs_cancelamento)

        messages.success(self.request, 'Evento ' + evento.nome + ' cancelado com sucesso')
        return super(EventoCancel, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, 'Erro no preenchimento: ' + str(form.errors))
        return super(EventoCancel, self).form_invalid(form, *args, **kwargs)


class EventoView(DetailView):
    # template_name = 'evento_detail.html'
    model = Evento

    def get_context_data(self, **kwargs):
        context = super(EventoView, self).get_context_data(**kwargs)
        coord = Coordenador.objects.get(user=self.request.user)
        aut = self.object.autorizacao_set.all()
        t_aut = self.object.eventotipoautorizacao_set.all()
        geradas = len(aut)
        aceitas = 0
        negadas = 0
        for a in aut:
            if a.autorizado:
                aceitas += 1
            else:
                negadas += 1
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        context['t_autorizacoes'] = t_aut
        context['autorizacoes'] = geradas
        context['aceitas'] = aceitas
        context['negadas'] = negadas
        return context


class EventoTipoAutorizacaoDelete(DeleteView):
    model = EventoTipoAutorizacao

    # success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(EventoTipoAutorizacaoDelete, self).get_context_data(**kwargs)
        coord = Coordenador.objects.get(user=self.request.user)
        self.object = self.get_object()
        evento = self.object.evento
        context['evento'] = evento
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, self.object.tipo_autorizacao.nome +
                         'excluído com sucesso do evento ' + self.object.evento.nome)
        url = reverse('evento-update', kwargs={'pk': self.object.evento.pk})
        return HttpResponseRedirect(url)


class AutorizacaoEventoList(ListView):
    model = Autorizacao

    def get_queryset(self):
        evento_id = self.kwargs['evento_id']
        aut = Autorizacao.objects.filter(evento=evento_id).order_by('-evento.data_evento')
        return aut

    def get_context_data(self, **kwargs):
        coord = Coordenador.objects.get(user=self.request.user)
        context = super(AutorizacaoEventoList, self).get_context_data(**kwargs)
        evento_id = self.kwargs['evento_id']
        evento = Evento.objects.get(pk=evento_id)
        autorizacoes = Autorizacao.objects.filter(evento=evento_id)
        groups = self.request.user.groups.all()
        autorizador = False
        coordenador = False
        for i in groups:
            if i.name == 'Autorizadores':
                autorizador = True
            if i.name == 'Coordenação':
                coordenador = True
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        context['autorizacoes'] = autorizacoes
        context['evento'] = evento
        context['is_autorizador'] = autorizador
        context['is_coordenador'] = coordenador
        return context


class MensagensList(ListView):
    template_name = 'message_list.html'

    def get_queryset(self):
        coord = Coordenador.objects.get(user=self.request.user)
        ev_un = EventoUnidade.objects.filter(ativo=True, unidade=coord.unidade,
                                             evento__data_cancelamento=None).order_by('data_criacao')
        solicitacoes = []
        for e in ev_un:
            if e.evento.gerador == 2:
                a = e.evento.autorizacao_set.first()
                solicitacoes.append(a)
        return solicitacoes

    def get_context_data(self, **kwargs):
        coord = Coordenador.objects.get(user=self.request.user)
        context = super(MensagensList, self).get_context_data(**kwargs)
        context['doc_title'] = 'Caixa de entrada'
        context['top_app_name'] = 'Solicitações'
        context['pt_h1'] = 'Caixa de entrada'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Solicitações'
        context['coordenador'] = coord
        return context


class AutorizacaoSuccess(TemplateView):
    template_name = 'success_auth_generation.html'

    def get_context_data(self, *args, **kwargs):
        coord = Coordenador.objects.get(user=self.request.user)
        context = super(AutorizacaoSuccess, self).get_context_data(**kwargs)
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        context['p_message'] = 'As autorizações estão em processamento! Retorne em alguns minutos.'
        context['tipo'] = 'scheduled'
        return context


class AutorizacaoScheduled(TemplateView):
    template_name = 'success_auth_generation.html'

    def get_context_data(self, *args, **kwargs):
        coord = Coordenador.objects.get(user=self.request.user)
        context = super(AutorizacaoScheduled, self).get_context_data(**kwargs)
        context['doc_title'] = 'Gestão de eventos'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos'
        context['pt_span'] = coord.name + ' - ' + coord.unidade.nome
        context['pt_breadcrumb2'] = 'Autorizações'
        context['p_message'] = 'As autorizações deste evento já estão sendo processadas! Retorne em alguns minutos.'
        context['tipo'] = 'scheduled'
        return context


class AutorizacaoView(DetailView):
    # template_name = 'evento_detail.html'
    model = Autorizacao

    def get_context_data(self, **kwargs):
        context = super(AutorizacaoView, self).get_context_data(**kwargs)
        groups = self.request.user.groups.all()
        autorizador = False
        coordenador = False
        for i in groups:
            if i.name == 'Autorizadores':
                autorizador = True
            if i.name == 'Coordenação':
                coordenador = True
        context['doc_title'] = 'Gestão de eventos' if coordenador else 'Área do usuário'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de eventos' if coordenador else 'Área do usuário'
        context['pt_breadcrumb2'] = 'Autorizações'
        context['pt_span'] = 'Detalhes de autorizações' if autorizador else ''
        context['is_autorizador'] = autorizador
        context['is_coordenador'] = coordenador
        context['status'] = 'Pendente'
        context['solicitacao'] = False
        if self.object.tipo.gerador == 1:
            if self.object.autorizado is not None:
                if self.object.autorizado:
                    messages.success(self.request, 'Esta atividade foi AUTORIZADA em ' +
                                     self.object.data_resposta_titular.strftime('%d/%m/%Y'))
                if not self.object.autorizado:
                    messages.error(self.request, 'Esta atividade foi NEGADA em ' +
                                   self.object.data_resposta_titular.strftime('%d/%m/%Y'))
            if self.object.revogado:
                messages.error(self.request, 'Esta autorização foi REVOGADA em ' +
                               self.object.data_revogacao.strftime('%d/%m/%Y'))
            if self.object.evento.is_canceled:
                messages.error(self.request, 'Esta atividade foi CANCELADA em ' +
                               self.object.evento.data_cancelamento.strftime('%d/%m/%Y'))
        else:
            context['solicitacao'] = True
            if coordenador:
                if self.object.autorizado is not None or self.object.autorizado is False:
                    aut = Autorizacao.objects.get(pk=self.kwargs['pk'])
                    aut.autorizar()
        return context


class AutorizacaoReleased(View):
    template_name = 'autorizacao_detail.html'

    def post(self, request, *args, **kwargs):
        aut = Autorizacao.objects.get(pk=self.request.POST.get('autorizacao', None))
        check = self.request.POST.get('inlineRadioOptions', None)
        if check == 'y':
            aut.autorizar()
        elif check == 'n':
            aut.recusar()
        elif check == 'r':
            aut.revogar()
        return redirect('autorizacao-released-success')


class AutorizacaoReleaseSuccess(TemplateView):
    template_name = 'success_auth_generation.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AutorizacaoReleaseSuccess, self).get_context_data(**kwargs)
        context['doc_title'] = 'Área do usuário'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Área do usuário'
        context['pt_span'] = 'Detalhes de autorizações'
        context['pt_breadcrumb2'] = 'Autorizações'
        context['p_message'] = 'Obrigado! Recebemos sua resposta.'
        context['is_autorizador'] = True
        context['tipo'] = 'aut'
        return context


class AutorizacaoGerar(View):
    def get(self, request, *args, **kwargs):
        evento = Evento.objects.get(pk=self.kwargs['pk'])
        tipos = []
        for item in evento.eventotipoautorizacao_set.all():
            tipos.append(item.tipo_autorizacao)

        check = ScheduledTask.objects.filter(gv_code=self.kwargs['pk'], task='generateAuth')
        if len(check) > 0:
            for i in check:
                if i.status == 'scheduled':
                    return redirect('evento-autorizacoes-scheduled')
                if i.status == 'completed':
                    return redirect('evento-autorizacoes-success')
        else:
            for item in tipos:
                st = ScheduledTask(task='generateAuth',
                                   status='scheduled',
                                   gv_code=self.kwargs['pk'],
                                   extra_field=item.pk)
                st.save()
            return redirect('evento-autorizacoes-success')


class AutorizacaoCreate(CreateView):
    model = Autorizacao
    form_class = AutorizacaoForm

    def get_context_data(self, **kwargs):
        context = super(AutorizacaoCreate, self).get_context_data(**kwargs)
        aut = Autorizador.objects.get(user=self.request.user)
        tp_aut = AutorizacoesModel.objects.get(pk=self.kwargs['pk'])
        context['doc_title'] = 'Área do Usuário'
        context['top_app_name'] = 'Autorizações'
        context['pt_h1'] = 'Gestão de Solicitações'
        context['pt_span'] = 'Nova Solicitação'
        context['pt_breadcrumb2'] = 'Área do usuário'
        context['tipo'] = tp_aut
        context['autorizador'] = aut
        context['dependentes'] = aut.aluno_set.filter(ativo=True)
        return context

    def form_valid(self, form, *args, **kwargs):
        tipo = AutorizacoesModel.objects.get(pk=self.request.POST.get('tipo', None))
        resp = Autorizador.objects.get(user=self.request.user)
        dt_inicio = self.request.POST.get('data_evento', None)
        dt_fim = self.request.POST.get('data_termino', None)
        aut = form.save(commit=False)
        evento = Evento(nome=tipo.nome + ' - ' + aut.aluno.nome,
                        descricao=self.request.POST.get('descricao', None),
                        data_evento=datetime.strptime(dt_inicio, "%d/%m/%Y").date(),
                        data_termino=datetime.strptime(dt_fim, "%d/%m/%Y").date(),
                        local_evento='N/A',
                        gerador=2,
                        aluno=aut.aluno,)
        evento.save()
        ev_un = EventoUnidade(evento=evento, unidade=aut.aluno.unidade)
        ev_un.save()
        aut.tipo = tipo
        aut.evento = evento
        aut.termos = tipo.texto
        aut.responsavel = resp
        aut.autorizado = False
        messages.success(self.request, 'Solicitação enviada com sucesso')
        return super(AutorizacaoCreate, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        print(form.errors)
        messages.error(self.request, 'Erro ao processar solicitação')
        return super(AutorizacaoCreate, self).form_invalid(form, *args, **kwargs)


class PrintAutReportView(View):
    def get(self, request, *args, **kwargs):
        report_type = self.kwargs['rpt_type']
        evento_id = self.kwargs['evento_id']
        evento = Evento.objects.get(pk=evento_id)
        autorizacoes = evento.autorizacao_set.all()
        tipos = []
        a_status = ''
        for a in autorizacoes:
            tipos.append(a.tipo)
        tipos = list(dict.fromkeys(tipos))  # Remover duplicatas

        if report_type == 0:
            autorizacoes = Autorizacao.objects.filter(evento=evento, autorizado=True, revogado=False, ativo=True)
            report_type = 'Concedidas'
        if report_type == 1:
            autorizacoes = Autorizacao.objects.filter(evento=evento, autorizado=False, ativo=True)
            report_type = 'Negadas'
        if report_type == 2:
            autorizacoes = Autorizacao.objects.filter(evento=evento, autorizado=None, ativo=True)
            report_type = 'Pendentes'
        if report_type == 3:
            report_type = 'Todos'

        response = HttpResponse(content_type='application/pdf')
        doc = SimpleDocTemplate(response, topMargin=2 * cm, rightMargin=2.5 * cm, leftMargin=2.5 * cm,
                                bottomMargin=2 * cm)

        # Style
        h1 = PS(
            name='Heading1',
            fontName='Times-Bold',
            alignment=TA_LEFT,
            fontSize=14,
            leading=14)

        h2 = PS(
            name='Heading2',
            fontName='Times-Bold',
            alignment=TA_CENTER,
            fontSize=12,
            leading=14)

        c1 = PS(
            name='Cell1',
            fontName='Times-Roman',
            alignment=TA_JUSTIFY,
            fontSize=10,
            leading=14)

        c2 = PS(
            name='Cell2',
            fontName='Times-Roman',
            alignment=TA_LEFT,
            fontSize=10,
            leading=14)

        c3 = PS(
            name='Cell1',
            fontName='Times-Bold',
            alignment=TA_JUSTIFY,
            fontSize=10,
            leading=14)

        n_session = 1

        # Body
        elements = [Paragraph(evento.nome, h2),
                    Spacer(1, 0.25 * cm),
                    Paragraph('Data: ' + evento.data_evento.strftime("%d/%m/%Y"), c1),
                    Spacer(1, 0.25 * cm),
                    Paragraph('Escopo: ' + evento.scope, c1),
                    Spacer(1, 0.25 * cm),
                    Paragraph(report_type, h2),
                    Spacer(1, 0.25 * cm)]

        if autorizacoes:
            for item in tipos:
                elements.append(Spacer(1, 0.25 * cm))
                elements.append(Paragraph(item.nome, c3))
                elements.append(Spacer(1, 0.25 * cm))
                for a in autorizacoes:
                    if a.cancelado is False:
                        if a.autorizado:
                            a_status = 'Autorizada em ' + a.data_resposta_titular.strftime("%d/%m/%Y")
                            if a.revogado:
                                a_status += ' e revogado em ' + a.data_revogacao.strftime("%d/%m/%Y")
                        elif a.autorizado is False:
                            a_status = 'Recusada em ' + a.data_resposta_titular.strftime("%d/%m/%Y")
                        elif a.autorizado is None:
                            a_status = 'Pendente'
                    else:
                        a_status = 'Cancelada'
                    if a.tipo == item:
                        day = a.data_modificacao.strftime("%d")
                        month = a.data_modificacao.strftime("%m")
                        year = a.data_modificacao.strftime("%Y")
                        data = [[Paragraph(a.aluno.nome.title(), c2),
                                 Paragraph(a_status, c1)]]
                        t = Table(data, colWidths=[180.0, 260.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                               ('INNERGRID', (0, 0), (2, 0), 0.10, black),
                                               ('BOX', (0, 0), (2, 0), 0.10, black),
                                               ]))
                        elements.append(t)
        else:
            elements = [Paragraph('Não há autorizações ' + report_type, h2),
                        Spacer(1, 0.25 * cm)]
        ###

        buffer = BytesIO()
        doc.title = evento.nome + ' - Lista de ' + report_type

        report = MyPrint(buffer, 'A4')

        # response.write(doc.build(elements))
        response.write(doc.build(elements, canvasmaker=NumberedCanvas))

        return response

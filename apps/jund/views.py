from django.views.generic import (
    TemplateView,
    CreateView
)
from apps.autorizacoes.models import (
    Evento,
    EventoTipoAutorizacao,
    AutorizacoesModel
)
from .forms import (
    EventoJundForm,
    InscricaoEventoForm
)
from .models import InscricaoEvento
from functions import (
    get_quotes,
    get_jund_member,
    calculate_age
)
from hermes import (
    send_jund_mail_subscription,
    send_jund_mail_authorization
)
from datetime import datetime
from django.contrib import messages


class JundIndexView(TemplateView):
    template_name = 'jund_index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(JundIndexView, self).get_context_data(**kwargs)
        day = datetime.now().day
        month = datetime.now().month
        quotes = get_quotes(day, month)
        quote = quotes[0].PENSAMENTO
        author = quotes[0].AUTORIA
        context['quote'] = quote
        context['author'] = author
        context['doc_title'] = 'Juventude Notre Dame'
        context['top_app_name'] = 'JUND'
        context['pt_h1'] = 'Juventude Notre Dame'
        context['pt_span'] = ' '
        context['pt_breadcrumb2'] = 'JUND'
        return context


class EventoJundCreate(CreateView):
    model = Evento
    form_class = EventoJundForm
    template_name = 'evento_jund_form.html'

    def get_context_data(self, **kwargs):
        context = super(EventoJundCreate, self).get_context_data(**kwargs)
        t_autorizacoes = AutorizacoesModel.objects.filter(ativo=True, gerador=1)
        day = datetime.now().day
        month = datetime.now().month
        quotes = get_quotes(day, month)
        quote = quotes[0].PENSAMENTO
        author = quotes[0].AUTORIA
        context['quote'] = quote
        context['author'] = author
        context['doc_title'] = 'Juventude Notre Dame'
        context['top_app_name'] = 'JUND'
        context['pt_h1'] = 'Juventude Notre Dame'
        context['pt_span'] = ' '
        context['pt_breadcrumb2'] = 'JUND'
        context['t_autorizacoes'] = t_autorizacoes
        return context

    def form_valid(self, form, *args, **kwargs):
        evento = form.save(commit=False)
        evento.ativo = True
        evento.gerador = 3
        evento.save()
        tipo = form.cleaned_data.get('tipo_autorizacao')
        # inclui as categorias de autorização que serão necessárias
        for i in tipo:
            ta = AutorizacoesModel.objects.get(pk=i.pk)
            tipos_evento = EventoTipoAutorizacao(tipo_autorizacao=ta,
                                                 evento=evento)
            tipos_evento.save()

        messages.success(self.request, 'Evento ' + evento.nome + ' criado com sucesso')
        return super(EventoJundCreate, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        print(form.errors)
        return super(EventoJundCreate, self).form_invalid(form, *args, **kwargs)


class InscricaoEventoJundCreate(CreateView):
    model = InscricaoEvento
    form_class = InscricaoEventoForm
    template_name = 'inscricao_evento_jund_form.html'

    # evento_id = self.kwargs['evento_id']
    def get_context_data(self, **kwargs):
        context = super(InscricaoEventoJundCreate, self).get_context_data(**kwargs)
        evento = Evento.objects.get(pk=self.kwargs['evento_id'])
        member = get_jund_member(self.kwargs['inscrito_id'], self.kwargs['tp_usr'])
        id_jund = member[0].ID
        nome = member[0].NOME
        email = member[0].EMAIL
        celular = member[0].CELULAR
        nascimento = member[0].NASCIMENTO
        cidade = member[0].CIDADE
        grupo = member[0].IDGRUPO
        idade = calculate_age(nascimento)
        day = datetime.now().day
        month = datetime.now().month
        quotes = get_quotes(day, month)
        quote = quotes[0].PENSAMENTO
        author = quotes[0].AUTORIA
        context['quote'] = quote
        context['author'] = author
        context['doc_title'] = 'Juventude Notre Dame'
        context['top_app_name'] = 'JUND'
        context['pt_h1'] = 'Juventude Notre Dame'
        context['pt_span'] = ' '
        context['pt_breadcrumb2'] = 'JUND'
        context['nome_i'] = nome
        context['email_i'] = email
        context['celular_i'] = celular
        context['nascimento_i'] = nascimento
        context['id_jund_i'] = id_jund
        context['evento'] = evento
        context['idade'] = idade
        context['cidade_i'] = cidade
        context['grupo_i'] = grupo
        return context

    def form_valid(self, form, *args, **kwargs):
        inscricao = form.save(commit=False)
        pk_evento = form.cleaned_data.get('evento_jund')
        pk_grupo = form.cleaned_data.get('id_grupo')
        evento = Evento.objects.get(pk=int(pk_evento))
        nsc = datetime.strptime(form.cleaned_data.get('nascimento'), '%d/%m/%Y')
        id_jund = form.cleaned_data.get('id_jund')
        inscricao.evento = evento
        inscricao.data_nascimento = nsc
        inscricao.id_jund = id_jund
        inscricao.id_grupo = pk_grupo
        inscricao.save()
        send_jund_mail_subscription(evento, inscricao)
        send_jund_mail_authorization(evento, inscricao)
        messages.success(self.request, f'Sua pré-inscrição está efetivada. Enviamos mais informações '
                                       f'para o seu e-mail {inscricao.email}')
        return super(InscricaoEventoJundCreate, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        print(form.errors)
        return super(InscricaoEventoJundCreate, self).form_invalid(form, *args, **kwargs)


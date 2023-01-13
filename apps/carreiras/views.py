from django.http import HttpResponseRedirect
from django.views.generic import (
    FormView,
    ListView,
    DetailView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import (
    Candidatura,
    Vaga,
    Escolaridade,
    Unidade,
    Area
)
from .forms import (
    CandidaturaForm,
    VagaForm,
    VagaEditForm,
    VagaSearchForm
)
from django.views.generic import (
    CreateView,
    UpdateView,
    View
)


class CarreirasFormView(FormView):
    template_name = 'carreiras_aplicar.html'
    form_class = CandidaturaForm
    success_url = reverse_lazy('carreiras')

    def get_context_data(self, **kwargs):
        vagas = Vaga.objects.filter(ativo=True, aberta=True)
        niveis = Escolaridade.objects.all()
        areas = Area.objects.all()
        unidades = Unidade.objects.all()
        cidades = []
        for item in unidades:
            cidades.append(item.cidade)

        cidades = list(dict.fromkeys(cidades))

        context = super(CarreirasFormView, self).get_context_data(**kwargs)
        context['doc_title'] = 'Trabalhe conosco'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'faça parte do nosso time!'
        context['pt_span'] = 'Cadastre-se e envie seu currículo'
        context['pt_breadcrumb2'] = 'Trabalhe conosco'
        context['vagas'] = vagas
        context['niveis'] = niveis
        context['areas'] = areas
        context['unidades'] = unidades
        context['cidades'] = cidades
        return context

    def form_valid(self, form, *args, **kwargs):
        apply = form.save(commit=False)
        if apply.cod_vaga:
            apply.cidade = apply.cod_vaga.unidade.cidade
            apply.area_interesse = apply.cod_vaga.area_interesse
            apply.unidade_interesse = apply.cod_vaga.unidade

        apply.ativo = True
        apply.consentimento_1 = True
        apply.consentimento_2 = True
        apply.consentimento_3 = True
        apply.save()
        form.send_mail(apply)
        messages.success(self.request, 'E-mail enviado com sucesso')
        return super(CarreirasFormView, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, 'Erro ao enviar e-mail')
        print(form.errors)
        return super(CarreirasFormView, self).form_invalid(form, *args, **kwargs)


class CarreirasList(ListView):
    model = Candidatura

    def get_context_data(self, **kwargs):
        context = super(CarreirasList, self).get_context_data(**kwargs)
        context['doc_title'] = 'Portal de Carreiras'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'Portal de carreiras'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Carreiras'
        return context

    def get_queryset(self):
        return Candidatura.objects.all()


class VagaCreate(CreateView):
    model = Vaga
    form_class = VagaForm

    def get_context_data(self, **kwargs):
        niveis = Escolaridade.objects.all()
        areas = Area.objects.all()
        unidades = Unidade.objects.all()

        context = super(VagaCreate, self).get_context_data(**kwargs)
        context['doc_title'] = 'Portal de Carreiras'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'Portal de carreiras'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Carreiras'
        context['niveis'] = niveis
        context['areas'] = areas
        context['unidades'] = unidades
        return context

    def form_valid(self, form, *args, **kwargs):
        vaga = form.save(commit=False)
        vaga.save()
        ax = vaga.area_interesse.nome[0:2].upper()
        bx = str(vaga.pk).zfill(5)
        cx = ''.join([x[0] for x in vaga.unidade.nome.split()])
        vaga.cod_vaga = ax + bx + cx
        vaga.save()

        messages.success(self.request, 'Vaga cadastrada')
        return super(VagaCreate, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, 'Erro ao cadastrar a vaga')
        return super(VagaCreate, self).form_invalid(form, *args, **kwargs)


class VagaView(DetailView):
    model = Vaga

    def get_context_data(self, **kwargs):
        context = super(VagaView, self).get_context_data(**kwargs)
        context['doc_title'] = 'Portal de Carreiras'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'Portal de carreiras'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Carreiras'
        return context


class VagaEdit(UpdateView):
    model = Vaga
    form_class = VagaEditForm
    template_name = 'carreiras/vaga_edit_form.html'

    def get_context_data(self, **kwargs):
        niveis = Escolaridade.objects.all()
        areas = Area.objects.all()
        unidades = Unidade.objects.all()

        context = super(VagaEdit, self).get_context_data(**kwargs)
        context['doc_title'] = 'Portal de Carreiras'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'Portal de carreiras'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Carreiras'
        context['niveis'] = niveis
        context['areas'] = areas
        context['unidades'] = unidades
        return context

    def form_valid(self, form, *args, **kwargs):
        messages.success(self.request, 'Vaga alterada')
        return super(VagaEdit, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, 'Erro ao alterar a vaga')
        return super(VagaEdit, self).form_invalid(form, *args, **kwargs)


class VagaDelete(DeleteView):
    model = Vaga
    success_url = reverse_lazy('index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.soft_delete():
            messages.success(self.request, 'Vaga excluída com sucesso!')
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.warning(self.request, self.object.msg_erro_exclusao)
            url = reverse('vaga-detail', kwargs={'pk': self.object.pk})
            return HttpResponseRedirect(url)


class VagaList(ListView):
    model = Vaga

    def get_queryset(self):
        vaga = Vaga.objects.filter(ativo=True).order_by('-data_criacao')
        return vaga

    def get_context_data(self, **kwargs):
        context = super(VagaList, self).get_context_data(**kwargs)
        context['doc_title'] = 'Portal de Carreiras'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'Portal de carreiras'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Carreiras'
        return context


class VagaFechar(View):
    def get(self, *args, **kwargs):
        vaga = Vaga.objects.get(pk=self.kwargs['pk'])
        vaga.close()
        messages.success(self.request, 'Vaga fechada')
        url = reverse('vaga-detail', kwargs={'pk': vaga.pk})
        return HttpResponseRedirect(url)


class CandidaturaList(ListView):
    model = Candidatura

    def get_queryset(self):
        cand = Candidatura.objects.filter(ativo=True).order_by('unidade_interesse', 'cod_vaga')
        return cand

    def get_context_data(self, **kwargs):
        context = super(CandidaturaList, self).get_context_data(**kwargs)
        context['doc_title'] = 'Portal de Carreiras'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'Portal de carreiras'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Carreiras'
        return context


class CandidaturaVagaList(ListView):
    model = Candidatura
    template_name = 'vaga_list.html'

    def get_queryset(self):
        vaga = Vaga.objects.get(pk=self.kwargs['pk'])
        cand = Candidatura.objects.filter(ativo=True, cod_vaga=vaga)
        return cand

    def get_context_data(self, **kwargs):
        context = super(CandidaturaVagaList, self).get_context_data(**kwargs)
        context['doc_title'] = 'Portal de Carreiras'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'Portal de carreiras'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Carreiras'
        return context


class CandidaturaView(DetailView):
    model = Candidatura

    def get_context_data(self, **kwargs):
        context = super(CandidaturaView, self).get_context_data(**kwargs)
        context['doc_title'] = 'Portal de Carreiras'
        context['top_app_name'] = 'Carreiras'
        context['pt_h1'] = 'Portal de carreiras'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Carreiras'
        return context

from django.shortcuts import render
from django.views.generic import TemplateView
from .models import (
    Paciente,
    Profissional,
    Evolucao,
    Afericoes,
    Medidas,
    Cuidados,
    Prescricao,
    Vacinacao
)


class ProntuarioView(TemplateView):
    template_name = 'prontuario.html'

    def get_context_data(self, **kwargs):
        context = super(ProntuarioView, self).get_context_data(**kwargs)
        id_paciente = self.kwargs['id_paciente']
        paciente = Paciente.objects.get(nd_code=id_paciente)
        evolucao = Evolucao.objects.filter(paciente_id=paciente.pk, ativo=True)
        afericoes = Afericoes.objects.filter(paciente_id=paciente.pk, ativo=True)
        medidas = Medidas.objects.filter(paciente_id=paciente.pk, ativo=True)
        cuidados = Cuidados.objects.filter(paciente_id=paciente.pk, ativo=True)
        prescricao = Prescricao.objects.filter(paciente_id=paciente.pk, ativo=True)
        vacinas = Vacinacao.objects.filter(paciente_id=paciente.pk, ativo=True)
        context['doc_title'] = 'Prontuário Digital'
        context['top_app_name'] = 'Saúde'
        context['pt_h1'] = 'Prontuário Digital'
        context['pt_span'] = 'Informações do paciente'
        context['pt_breadcrumb2'] = 'Prontuário Digital'
        context['paciente'] = paciente
        context['evolucao'] = evolucao
        context['afericoes'] = afericoes
        context['medidas'] = medidas
        context['cuidados'] = cuidados
        context['prescricao'] = prescricao
        context['vacinas'] = vacinas


        return context

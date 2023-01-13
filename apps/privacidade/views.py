from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContactForm


class PrivacidadeFormView(FormView):
    template_name = 'privacidade.html'
    form_class = ContactForm
    success_url = reverse_lazy('privacidade')

    def get_context_data(self, **kwargs):
        context = super(PrivacidadeFormView, self).get_context_data(**kwargs)
        context['doc_title'] = 'Privacidade'
        context['top_app_name'] = 'Privacidade'
        context['pt_h1'] = 'Política de Privacidade e Proteção de Dados'
        context['pt_span'] = 'Nós levamos a sério a sua privacidade'
        context['pt_breadcrumb2'] = 'Privacidade'
        return context

    def form_valid(self, form, *args, **kwargs):
        form.send_mail()
        messages.success(self.request, 'E-mail enviado com sucesso')
        return super(PrivacidadeFormView, self).form_valid(form, *args, **kwargs)

    def form_invalid(self, form, *args, **kwargs):
        messages.error(self.request, 'Erro ao enviar e-mail')
        return super(PrivacidadeFormView, self).form_invalid(form, *args, **kwargs)
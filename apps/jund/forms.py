from django import forms
from .models import InscricaoEvento
from functions import validate
from apps.autorizacoes.models import (
    Evento,
    AutorizacoesModel,
)


class EventoJundForm(forms.ModelForm):
    tipo_autorizacao = forms.ModelMultipleChoiceField(queryset=AutorizacoesModel.objects.all(),
                                                      widget=forms.SelectMultiple)

    class Meta:
        model = Evento
        fields = ['nome',
                  'descricao',
                  'data_evento',
                  'data_termino',
                  'local_evento',
                  ]


class InscricaoEventoForm(forms.ModelForm):
    evento_jund = forms.CharField(max_length=20)
    nascimento = forms.CharField(max_length=20)
    id_jund = forms.IntegerField()
    id_grupo = forms.IntegerField()

    class Meta:
        model = InscricaoEvento
        fields = ['nome',
                  'email',
                  'cidade',
                  'telefone',
                  'nome_responsavel',
                  'email_responsavel',
                  'cpf_responsavel',
                  'restricoes']

    def clean(self):
        # data from the form is fetched using super function
        super(InscricaoEventoForm, self).clean()
        evento = Evento.objects.get(pk=self.cleaned_data.get('evento_jund'))
        cpf = self.cleaned_data.get('cpf_responsavel')
        id_jund = self.cleaned_data.get('id_jund')
        v_email = self.cleaned_data.get('email')
        check = InscricaoEvento.objects.filter(evento=evento, id_jund=id_jund, email=v_email)
        if check:
            self._errors['nome'] = self.error_class([
                f'Sua inscrição para o evento já foi enviada anteriormente. Verifique seu e-mail'])
        if not validate(cpf):
            self._errors['cpf_responsavel'] = self.error_class([
                f'O número {cpf} não é um CPF válido. Verifique o número e tente novamente'])
        # return any errors if found
        return self.cleaned_data

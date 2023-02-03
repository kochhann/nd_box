from django import forms
from .models import (
    Evento,
    AutorizacoesModel,
    Autorizacao,
    AnexoAutorizacao
)


class EventoForm(forms.ModelForm):
    tipo_autorizacao = forms.ModelMultipleChoiceField(queryset=AutorizacoesModel.objects.all(),
                                                      widget=forms.SelectMultiple)

    class Meta:
        model = Evento
        fields = '__all__'

    # this function will be used for the validation
    def clean(self):

        # data from the form is fetched using super function
        super(EventoForm, self).clean()
        count = 0
        check = [self.cleaned_data.get('aluno'),
                 self.cleaned_data.get('turma'),
                 self.cleaned_data.get('ciclo'),
                 self.cleaned_data.get('curso'),
                 self.cleaned_data.get('unidade')]
        nome = self.cleaned_data.get('nome')
        for item in check:
            if item is None:
                count += 1

        if count == 5:
            self._errors['aluno'] = self.error_class([
                'Defina o escopo para o evento!'])

        if count < 4:
            self._errors['aluno'] = self.error_class([
                'Escolha apenas UM escopo para o evento!'])

        # return any errors if found
        return self.cleaned_data


class EventoEditForm(forms.ModelForm):
    tipo_autorizacao = forms.ModelMultipleChoiceField(queryset=AutorizacoesModel.objects.all(),
                                                      widget=forms.SelectMultiple,
                                                      required=False)

    class Meta:
        model = Evento
        fields = ['nome', 'data_evento', 'data_termino', 'local_evento', 'descricao']


class EventoCancelForm(forms.ModelForm):

    class Meta:
        model = Evento
        fields = ['obs_cancelamento']


class AutorizacaoForm(forms.ModelForm):
    tipo = forms.CharField(label='Tipo')
    data_evento = forms.DateField(label='Data início')
    data_termino = forms.DateField(label='Data fim')
    descricao = forms.CharField(label='Descrição')

    class Meta:
        model = Autorizacao
        fields = ['aluno']


class AnexoAutorizacaoForm(forms.ModelForm):
    class Meta:
        model = AnexoAutorizacao
        fields = ['arquivo', 'descricao']


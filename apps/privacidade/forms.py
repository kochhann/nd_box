from django import forms
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class ContactForm(forms.Form):
    SUBJECT = [
        (None, '-- Finalidade do contato --'),
        ('1', 'Acessar meus dados pessoais'),
        ('2', 'Receber meus dados pessoais em formato simplificado'),
        ('3', 'Retificar meus dados pessoais'),
        ('4', 'Solicitar a exclusão dos meus dados pessoais'),
        ('5', 'Confirmar a existência de tratamento dos meus dados pessoais'),
        ('6', 'Outros'),
    ]
    name = forms.CharField(label='Nome', max_length=100)
    email = forms.EmailField(label='E-mail', max_length=100)
    subject = forms.ChoiceField(label='Assunto', choices=SUBJECT)
    message = forms.CharField(label='Mensagem', widget=forms.Textarea())

    def send_mail(self):
        subject = self.cleaned_data['subject']
        subject = dict(self.fields['subject'].choices)[subject]
        email_template_name = 'email/privacy_request.html'
        m_context = {
            "name": self.cleaned_data['name'],
            "email": self.cleaned_data['email'],
            "message": self.cleaned_data['message'],
            "sender": 'Privacidade'
        }
        email = render_to_string(email_template_name, m_context)
        subject = subject
        from_email = '"Sistema ND Box | Privacidade" <contato@nd.org.br>'
        to = 'dpo@nd.org.br'
        msg = EmailMultiAlternatives(subject, email, from_email, [to])
        msg.attach_alternative(email, "text/html")

        msg.send()

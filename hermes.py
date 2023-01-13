import datetime
import re
import requests
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from decouple import config


def send_registration_request(form):
    email_template_name = 'email/registration_request.html'
    m_context = {
        "name": form.cleaned_data['register_name'],
        "email": form.cleaned_data['register_email'],
        "r_id": form.cleaned_data['register_id'],
        "sender": 'Registro'
    }
    email = render_to_string(email_template_name, m_context)
    subject = 'Solicitação de registro no sistema ND Box'
    from_email = '"Sistema ND Box" <contato@nd.org.br>'
    to = form.cleaned_data['register_email']
    msg = EmailMultiAlternatives(subject, email, from_email, [to])
    msg.attach_alternative(email, "text/html")

    msg.send()


def send_not_user(form):
    email_template_name = 'email/user_dont_exists.html'
    m_context = {
        "name": form.cleaned_data['register_name'],
        "email": form.cleaned_data['register_email'],
        "r_id": form.cleaned_data['register_id'],
        "sender": 'Registro'
    }
    email = render_to_string(email_template_name, m_context)
    subject = 'Solicitação de registro no sistema ND Box'
    from_email = '"Sistema ND Box" <contato@nd.org.br>'
    to = form.cleaned_data['register_email']
    msg = EmailMultiAlternatives(subject, email, from_email, [to])
    msg.attach_alternative(email, "text/html")

    msg.send()


def send_not_relative(form):
    email_template_name = 'email/user_not_relative.html'
    m_context = {
        "name": form.cleaned_data['register_name'],
        "email": form.cleaned_data['register_email'],
        "r_id": form.cleaned_data['register_id'],
        "sender": 'Registro'
    }
    email = render_to_string(email_template_name, m_context)
    subject = 'Solicitação de registro no sistema ND Box'
    from_email = '"Sistema ND Box" <contato@nd.org.br>'
    to = form.cleaned_data['register_email']
    msg = EmailMultiAlternatives(subject, email, from_email, [to])
    msg.attach_alternative(email, "text/html")

    msg.send()


def send_cancel_mail(evento, responsavel):
    email_template_name = 'email/event_canceled.html'
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    m_context = {
        "evento": evento.nome,
        "motivo": evento.obs_cancelamento,
        "data_evento": evento.data_evento.strftime("%d/%m/%Y"),
        "sender": 'Eventos'

    }
    email = render_to_string(email_template_name, m_context)
    subject = 'Rede Notre Dame - Aviso de cancelamento de evento'
    from_email = '"Sistema ND Box" <contato@nd.org.br>'
    # to = 'apoio.ti@nd.org.br'
    to = responsavel.email
    msg = EmailMultiAlternatives(subject, email, from_email, [to])
    msg.attach_alternative(email, "text/html")

    msg.send()


def send_test_mail():
    email_template_name = 'email/mensagem_teste.html'
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    m_context = {
        "date": date
    }
    email = render_to_string(email_template_name, m_context)
    subject = 'Teste do sistema ND Box'
    from_email = '"Sistema ND Box" <contato@nd.org.br>'
    to = 'juliano@Kochhann.com.br'
    msg = EmailMultiAlternatives(subject, email, from_email, [to])
    msg.attach_alternative(email, "text/html")

    msg.send()


def send_welcome_mail(responsavel):
    email_template_name = 'email/welcome_message.html'
    m_context = {
        "responsavel": responsavel
    }
    email = render_to_string(email_template_name, m_context)
    subject = 'Rede Notre Dame - Confirmação de cadastro'
    from_email = '"Sistema ND Box" <contato@nd.org.br>'
    to = 'apoio.ti@nd.org.br'
    # to = responsavel.email
    msg = EmailMultiAlternatives(subject, email, from_email, [to])
    msg.attach_alternative(email, "text/html")

    msg.send()

def send_jund_mail_subscription(evento, inscricao):
    email_template_name = 'email/jund_subscription_confirmation.html'
    m_context = {
        "evento": evento,
        "inscricao": inscricao,
        "sender": 'Eventos Juventude Notre Dame'
    }
    email = render_to_string(email_template_name, m_context)
    subject = 'Rede Notre Dame - Inscrição em evento Juventude Notre Dame'
    from_email = '"Sistema ND Box" <contato@nd.org.br>'
    to = inscricao.email
    msg = EmailMultiAlternatives(subject, email, from_email, [to])
    msg.attach_alternative(email, "text/html")

    msg.send()


def send_jund_mail_authorization(evento, inscricao):
    email_template_name = 'email/jund_subscription_authorization.html'
    t_autorizacao = evento.eventotipoautorizacao_set.all()
    for aut in t_autorizacao:
        autorizacao = aut.tipo_autorizacao

        print(autorizacao.nome)
        m_context = {
            "evento": evento,
            "inscricao": inscricao,
            "autorizacao": autorizacao,
            "sender": 'Eventos Juventude Notre Dame'
        }
        email = render_to_string(email_template_name, m_context)
        subject = 'Rede Notre Dame - Autorização para evento da Juventude Notre Dame'
        from_email = '"Sistema ND Box" <contato@nd.org.br>'
        to = inscricao.email_responsavel
        msg = EmailMultiAlternatives(subject, email, from_email, [to], reply_to=['jund@nd.org.br'])
        msg.attach_alternative(email, "text/html")

        msg.send()


def send_nd_mail(message):
    email_template_name = 'email/mail_nd.html'
    regex = re.compile(r'^[a-zA-Z0-9_.-]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+$')
    if re.fullmatch(regex, message.email_destino):
        email = f'<span>ND Box | Sistema ND</span>' \
                f'<p>{message.mensagem}</p>' \
                f'<br><p>Caso não reconheça o conteúdo desta mensagem, encaminhe este e-mail para' \
                f' projeto@nd.org.br.</p>' \
                f'<br><b>Sistema ND - Associação Notre Dame</b>'
        subject = message.assunto
        from_email = '"Sistema ND Box" <contato@nd.org.br>'
        to = message.email_destino
        # to = 'apoio.ti@nd.org.br'
        msg = EmailMultiAlternatives(subject, email, from_email, [to], reply_to=[message.email_remetente])
        msg.attach_alternative(email, "text/html")
    else:
        m_context = {
            "mail_destino": message.email_destino,
            "mail_remetente": message.email_remetente,
            "mail_assunto": message.assunto,
            "usuario": message.usuario or 'Não consta',
            "data_geracao": message.data_geracao,
            "sender": 'Sistema ND'
        }
        email = render_to_string(email_template_name, m_context)
        subject = 'Erro em envio de mensagem'
        from_email = '"Sistema ND Box" <contato@nd.org.br>'
        to = [message.email_remetente, 'projeto@nd.org.br']
        msg = EmailMultiAlternatives(subject, email, from_email, to, reply_to=[message.email_remetente])
        msg.attach_alternative(email, "text/html")

    msg.send()


def send_comtele(sender_id, receiver, message):
    # sender_id = 01 para envio de boletos
    auth_key = config('COMTELE-KEY')
    url = "https://sms.comtele.com.br/api/v2/send"
    msg = f'Comunicado ND{message}'
    payload = "{\"Sender\":\"" + sender_id + "\",\"Receivers\":\"" + receiver + "\",\"Content\":\"" + msg + "\"}"
    headers = {
        'content-type': "application/json",
        'auth-key': auth_key
    }
    print(f'chave - {auth_key}')

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)

from django import forms
from hermes import (
    send_registration_request,
    send_not_user,
    send_not_relative
)


class RegistrationForm(forms.Form):
    register_name = forms.CharField(label='Nome')
    register_email = forms.EmailField(label='E-mail')
    register_id = forms.CharField(label='CPF')

    def send_registration(self):
        send_registration_request(self)

    def send_not_user(self):
        send_not_user(self)

    def send_not_relative(self):
        send_not_relative(self)

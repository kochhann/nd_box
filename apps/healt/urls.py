from django.urls import path
from .views import ProntuarioView


urlpatterns = [
    path('<int:id_paciente>/', ProntuarioView.as_view(), name='prontuario_view')
]
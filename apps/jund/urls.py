from django.urls import path
from apps.jund.views import (
    JundIndexView,
    EventoJundCreate,
    InscricaoEventoJundCreate
)

urlpatterns = [
    path('', JundIndexView.as_view(), name='jund'),
    path('evento/create/', EventoJundCreate.as_view(), name='evento-jund-create'),
    path('inscricao/create/<int:evento_id>/<int:inscrito_id>/<int:tp_usr>', InscricaoEventoJundCreate.as_view(),
         name='inscricao-evento-jund-create'),
]

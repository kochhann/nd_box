from django.urls import path
from .views import (
    CarreirasFormView,
    VagaCreate,
    VagaView,
    VagaEdit,
    VagaDelete,
    VagaList,
    VagaFechar,
    CandidaturaList,
    CandidaturaView,
    CandidaturaVagaList,
)

urlpatterns = [
    path('lista_aplicacoes', CandidaturaList.as_view(), name='aplicacoes-list'),
    path('', CarreirasFormView.as_view(), name='carreiras'),
    path('vaga/create/', VagaCreate.as_view(), name='vaga-create'),
    path('vaga/<int:pk>/', VagaView.as_view(), name='vaga-detail'),
    path('vaga/update/<int:pk>/', VagaEdit.as_view(), name='vaga-update'),
    path('vaga/delete/<int:pk>/', VagaDelete.as_view(), name='vaga-delete'),
    path('vaga/list/', VagaList.as_view(), name='vaga-list'),
    path('vaga/fechar/<int:pk>/', VagaFechar.as_view(), name='vaga-fechar'),
    path('candidatura/<int:pk>/', CandidaturaView.as_view(), name='candidatura-detail'),
    path('candidatura/vaga/<int:pk>/', CandidaturaVagaList.as_view(), name='candidatura-vaga')
]

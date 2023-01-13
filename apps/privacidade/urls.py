from django.urls import path
from .views import PrivacidadeFormView

urlpatterns = [
    path('', PrivacidadeFormView.as_view(), name='privacidade'),
]

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import static


urlpatterns = [
    path('', include('apps.core.urls')),
    path('manager/', admin.site.urls),
    path('carreiras/', include('apps.carreiras.urls')),
    path('reports/', include('apps.reports.urls')),
    path('privacidade/', include('apps.privacidade.urls')),
    path('autorizacoes/', include('apps.autorizacoes.urls')),
    path('healt/', include('apps.healt.urls')),
    path('jund/', include('apps.jund.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.site.site_header = 'Gestão ND Box'
admin.site.site_title = 'Gestão ND Box'
admin.site.index_title = 'Área Administrativa'

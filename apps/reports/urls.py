from django.urls import path
from .views import ReportsView, PrintCoverView, PrintStatisticsView

urlpatterns = [
    path('<int:id_annals>/<int:id_house>/<slug:slctd_year>/', ReportsView.as_view(), name='reports'),
    path('printCover/<int:id_house>/<slug:slctd_year>/', PrintCoverView.as_view(), name='print_cover'),
    path('printStatistics/<int:id_annals>/<int:id_house>/<slug:slctd_year>/', PrintStatisticsView.as_view(),
         name='print_statistics'),
]

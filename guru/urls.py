from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('guru-piket/', views.izin_guru_view, name='izin_guru'),
    path('guru-piket/tindakan/<str:izin_id>/', views.tindakan_izin_view, name='tindakan_izin'),
    path('guru-piket/proses-tindakan/<str:izin_id>/', views.proses_tindakan_view, name='proses_tindakan'),
]
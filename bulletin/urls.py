from django.urls import path
from .views import *

urlpatterns = [
    path('',index, name='bulletin'),
    path('/<int:classe_id>/moyenne', get_classe_moyenne, name='moyenne_eleve'),
    path('telecharger-bulletin-eleve/<int:eleve_id>', download_bul_student, name='download_bul_student')
]
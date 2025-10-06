from django.urls import path
from .views import *

urlpatterns = [
    path('',connexion, name='login'),
    path('deconnexion/', logoutPage, name='logout'),

]

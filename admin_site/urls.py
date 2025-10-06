from django.urls import path
from .views import *

urlpatterns = [
    path('',index, name='index'),
    path('classes/', liste_classe, name='list_classe'),
    path('classes/<int:pk>/modifier', UpdateClasse.as_view(), name='update_classe'),
    path('classes/<int:pk>/supprimer', DeleteClasse.as_view(), name='delete_classe'),

    path('matieres/', liste_matiere, name='list_matiere'),
    path('eleves/', list_eleve, name='list_eleve'),
    path('eleves/ajouter-un-eleve/', create_student, name="create_eleve"),

    path('enseignants/', ListEnseignant.as_view(), name='list_enseignant'),
    path('enseignants/ajouter-un-enseignant/', create_teacher, name="create_enseignant"),

    path('notes/', get_note, name='list_note'),
    path('notes/<int:classe_id>/remplissage', add_note, name='add_note'),
    path('notes/liste/', get_liste_note, name="liste_note"),
]

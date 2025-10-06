from django.shortcuts import render, get_object_or_404
from admin_site.models import *
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    context = {
        'eleve':Eleve.objects.count(),
        'enseignant':Enseignant.objects.count(),
        'classes':Classe.objects.all()
    }
    return render(request, 'classes.html', context)

def get_classe_moyenne(request, classe_id):
    # On récupère l'évaluation : (matière + classe + séquence)
    classe = get_object_or_404(Classe, id=classe_id)
    # On récupère tous les élèves de la classe liée à cette évaluation
    eleves = Eleve.objects.filter(classe=classe_id)

    return render(request, "moyenne_eleve.html", {
        "classe": classe,
        "eleves": eleves,
    })

def download_bul_student(request, eleve_id):
   return render(request, 'bulletin.html') 
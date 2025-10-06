from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .models import *
from .form import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin



# Create your views here.
@login_required
def index(request):
   context={
       'eleve':Eleve.objects.count(),
       'enseignant':Enseignant.objects.count(),
   }
   return render (request, 'dashboard.html', context)

# gestion des classes
@login_required
def liste_classe(request):
    classes = Classe.objects.all()
    if request.method == "POST":
        form=ClasseForm(request.POST)
        if form.is_valid():
            # form.save()
            Classe.objects.create(
               libelle = form.cleaned_data['libelle'],
               code =form.cleaned_data['code'] 
            )
            messages.success(request, "La classe a été ajoutée avec succès !")
    else : 
        form = ClasseForm()
    context = {
        'form':form,
        'classes':classes
    }
    return render(request, 'classes/liste.html', context)

class UpdateClasse(LoginRequiredMixin,UpdateView):
    model = Classe
    form_class = ClasseForm
    template_name = 'classes/update.html'  # ou ton chemin réel
    success_url = reverse_lazy('list_classe')

    def put(self, request, *args, **kwargs):
      response = super().put(request, *args, **kwargs)
      message = messages.success(self.request, "La classe a été mofifier avec succès")
      reponses = [response,message]
      return reponses

class DeleteClasse(LoginRequiredMixin,DeleteView):
   model = Classe
   template_name = "classes/delete.html"
   success_url = reverse_lazy('list_classe')

   def delete(self, request, *args, **kwargs):
      response = super().delete(request, *args, **kwargs)
      message = messages.success(self.request, "La classe a été supprimé avec succès")
      reponses = [response,message]
      return reponses

# gestion des matieres
@login_required
def liste_matiere(request):
    if request.method == "POST":
        form=MatiereRigisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La matiere a été ajoutée avec succès !")
    else : 
        form = MatiereRigisterForm()
    matieres = Matiere.objects.all()
    context={
        'matieres':matieres,
        'form':form
    }
    return render(request, 'matieres/liste.html', context)

# gestion enseignants
class ListEnseignant(LoginRequiredMixin,ListView):
    model=Enseignant
    context_object_name = 'enseignants'
    template_name = "enseignants/liste.html"

@login_required
def create_teacher(request):
    if request.method == "POST":
        form = TeacherRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Enseignant enregistrer avec succès !")
            return redirect('list_enseignant')
    else:
        form = TeacherRegisterForm()
    return render(request, "enseignants/create.html", {'form':form})

# gestion enseignants
def list_eleve(request):
   eleves = Eleve.objects.all()
   classes  = Classe.objects.all()
   context = {
       'eleves':eleves,
       'classes':classes
   }
   return render(request, 'eleves/liste.html', context)

@login_required
def create_student(request):
    if request.method == "POST":
        form = EleveRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Élève enregistrer avec succès !")
            return redirect('list_eleve')
    else:
        form = EleveRegisterForm()
    return render(request, "eleves/create.html", {'form':form})

@login_required
def get_note(request):

    context={
        'classes':Classe.objects.all()
    }
    return render(request, "notes/liste.html", context)

@login_required
def add_note(request, classe_id):
    # On récupère l'évaluation : (matière + classe + séquence)
    classe = get_object_or_404(Classe, id=classe_id)
    # On récupère tous les élèves de la classe liée à cette évaluation
    eleves = Eleve.objects.filter(classe=classe_id)

    matieres=Matiere.objects.filter(classe=classe_id)

    if request.method == "POST":
        matiere_id = request.POST.get("matiere")
        sequence = request.POST.get("sequence")

        # Vérifier si une évaluation existe déjà
        evaluation, created = Evaluation.objects.get_or_create(
            matiere_id=matiere_id,
            classe=classe,
            type_evaluation=sequence
        )

        # Enregistrer les notes
        for eleve in eleves:
            note_val = request.POST.get(f"note_{eleve.id}")
            if note_val:
                # Mettre à jour si la note existe déjà, sinon créer
                Note.objects.update_or_create(
                    evaluation=evaluation,
                    eleve=eleve,
                    defaults={"note": note_val}
                )

        return redirect('liste_note')

    return render(request, "notes/ajouter_note.html", {
        "classe": classe,
        "eleves": eleves,
        "matieres":matieres,
    })

@login_required
def get_liste_note(request):
    classe = request.GET.get("classe")
    matiere = request.GET.get("matiere")
    sequence = request.GET.get("sequence")
    eleves = Eleve.objects.filter(classe=classe)

    notes_par_eleve = {}

    if classe and matiere and sequence:
        classe = Classe.objects.get(id=classe)
        matiere = Matiere.objects.get(id=matiere)
        eleves = Eleve.objects.filter(classe=classe)
    # Récupérer l’évaluation correspondante
        try:
            evaluation = Evaluation.objects.get(classe=classe, matiere=matiere, type_evaluation=sequence)
        except Evaluation.DoesNotExist:
                evaluation = None

        if evaluation:
                notes_dict = {n.eleve_id: n.note for n in evaluation.notes.all()}

                for eleve in eleves:
                    eleve.note = notes_dict.get(eleve.id, "-")

    context = {
        "classe": classe,
        "matiere": matiere,
        "sequence": sequence,
        "eleves": eleves,
        "notes_par_eleve": notes_par_eleve,
        "matieres":Matiere.objects.all(),
        'evaluation':evaluation
    }

    return render(request, "notes/notes_eleves.html", context)
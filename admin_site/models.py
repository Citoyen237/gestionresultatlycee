from django.db import models
from auth_app.models import CustomUser

# Create your models here.
class Classe(models.Model):
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)  

    class Meta:
        unique_together = ('libelle', 'code')

    @property
    def eleve(self):
        return self.eleves.count()

    def __str__(self):
        return f'{self.libelle}({self.code})' 
    

class Eleve(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="eleve_profile")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="eleves")
    date_naissance = models.DateField(blank=True, null=True)
    nom_pere = models.CharField(max_length=255)
    nom_mere = models.CharField(max_length=255)
    email_parent = models.EmailField()
    phone_parent = models.CharField(max_length=200)
    password=models.CharField(max_length=200)


    def __str__(self):
        return f"{self.user.get_full_name()}"


class Enseignant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="enseignant_profile")
    grade = models.CharField(max_length=100)
    matiere = models.CharField(max_length=100)  # ex: "Mathématiques"
    phone_number = models.CharField(max_length=200)
    password=models.CharField(max_length=200)


    def __str__(self):
        return f"{self.user.get_full_name()}"

class Matiere(models.Model):
    nom = models.CharField(max_length=100)  # Ex: Mathématiques, Physique
    coefficient = models.PositiveIntegerField(default=1)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, null=True, blank=True, related_name='enseignant_matiere')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nom

class Evaluation(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name="evaluations")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="evaluations")
    type_evaluation = models.CharField(max_length=50, choices=[
        ("1", "Sequence 1"),
        ("2", "Sequence 2"),
    ])
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('classe', 'matiere', 'type_evaluation')
    
    def __str__(self):
        return f'sequence {self.type_evaluation}/{self.matiere}/{self.classe}'
    
class Note(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name="notes")
    note = models.DecimalField(max_digits=5, decimal_places=2)
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="notes")






# class Bulletin(models.Model):
#     eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="bulletins")
#     trimestre = models.CharField(max_length=50, choices=[
#         ("T1", "Trimestre 1"),
#         ("T2", "Trimestre 2"),
#         ("T3", "Trimestre 3"),
#     ])
#     annee_scolaire = models.CharField(max_length=20)  # Ex: 2024-2025
#     date_creation = models.DateTimeField(auto_now_add=True)

#     def moyenne_generale(self):
#         notes = self.eleve.evaluations.all()
#         if not notes.exists():
#             return 0
#         total = sum([n.note * n.matiere.coefficient for n in notes])
#         coef = sum([n.matiere.coefficient for n in notes])
#         return round(total / coef, 2)

#     def __str__(self):
#         return f"Bulletin {self.eleve} - {self.trimestre} {self.annee_scolaire}"

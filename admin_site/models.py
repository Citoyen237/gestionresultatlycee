from django.db import models
from auth_app.models import CustomUser
from decimal import Decimal


# Create your models here.
class Classe(models.Model):
    libelle = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)  

    class Meta:
        unique_together = ('libelle', 'code')

    @property
    def eleve(self):
        return self.eleves.count()
    
    @property
    def moyenne_generale(self):
        """
        Calcule la moyenne générale de la classe pour une séquence donnée
        """
        eleves = self.eleves.all()
        
        if not eleves.exists():
            return 0
        
        total_moyennes = Decimal('0')
        nb_eleves = 0
        
        for eleve in eleves:
            moyenne = eleve.moyenne
            if moyenne > 0:  # Ne compter que les élèves qui ont des notes
                total_moyennes += Decimal(moyenne)
                nb_eleves += 1
        
        if nb_eleves == 0:
            return 0
        
        return round(total_moyennes / nb_eleves, 2)
    
    @property
    def pourcentage_reussite(self):
        """
        Calcule le pourcentage de réussite de la classe pour une séquence donnée
        seuil: note minimale pour considérer qu'un élève a réussi (par défaut 10/20)
        """
        seuil=10
        eleves = self.eleves.all()
        
        if not eleves.exists():
            return 0
        
        nb_eleves_avec_notes = 0
        nb_reussis = 0
        
        for eleve in eleves:
            moyenne = eleve.moyenne
            if moyenne > 0:  # Élève ayant au moins une note
                nb_eleves_avec_notes += 1
                if moyenne >= seuil:
                    nb_reussis += 1
        
        if nb_eleves_avec_notes == 0:
            return 0
        
        return round((nb_reussis / nb_eleves_avec_notes) * 100, 2)
    
    
    @property
    def rang(self):
        """
        Retourne le rang de cette classe parmi toutes les classes
        Pour la séquence 1
        """
        try:
            # Récupérer toutes les classes
            toutes_classes = Classe.objects.all()
            
            if not toutes_classes.exists():
                return None
            
            # Calculer les moyennes de toutes les classes
            moyennes_classes = []
            for classe in toutes_classes:
                try:
                    moyenne = classe.moyenne_generale
                    # S'assurer que c'est un nombre
                    moyenne = float(moyenne) if moyenne else 0
                except Exception:
                    moyenne = 0
                
                moyennes_classes.append({
                    'classe_id': classe.id,
                    'moyenne': moyenne
                })
            
            # Trier par moyenne décroissante
            moyennes_classes.sort(key=lambda x: float(x['moyenne']), reverse=True)
            
            # Trouver le rang de la classe actuelle
            for i, item in enumerate(moyennes_classes, 1):
                if item['classe_id'] == self.id:
                    return i
            
            return None
        except Exception as e:
            print(f"Erreur dans le calcul du rang: {e}")
            return None
        
    @property
    def meilleur_eleve(self):
        """
        Retourne le meilleur élève de la classe pour une séquence donnée
        Retourne un dictionnaire avec les infos de l'élève
        """
        eleves = self.eleves.all()
        
        if not eleves.exists():
            return None
        
        # Calculer les moyennes de tous les élèves
        eleves_moyennes = []
        for eleve in eleves:
            moyenne = eleve.moyenne
            if moyenne > 0:  # Uniquement les élèves qui ont des notes
                eleves_moyennes.append({
                    'eleve': eleve,
                    'moyenne': moyenne
                })
        
        if not eleves_moyennes:
            return None
        
        # Trier par moyenne décroissante et prendre le premier
        eleves_moyennes.sort(key=lambda x: x['moyenne'], reverse=True)
        
        meilleur = eleves_moyennes[0]
        return {
            'eleve': meilleur['eleve'],
            'nom': meilleur['eleve'].user.get_full_name(),
            'moyenne': meilleur['moyenne'],
            'mention': meilleur['eleve'].mention
        }

    def statistiques_sequence(self, type_sequence="1"):
        """
        Retourne les statistiques complètes de la classe pour une séquence
        """
        eleves = self.eleves.all()
        
        if not eleves.exists():
            return {
                'moyenne_generale': 0,
                'moyenne_max': 0,
                'moyenne_min': 0,
                'pourcentage_reussite': 0,
                'nb_eleves_total': 0,
                'nb_eleves_admis': 0,
                'nb_eleves_ajournes': 0
            }
        
        moyennes = []
        for eleve in eleves:
            moyenne = eleve.moyenne_sequence(str(type_sequence))
            if moyenne > 0:
                moyennes.append(moyenne)
        
        if not moyennes:
            return {
                'moyenne_generale': 0,
                'moyenne_max': 0,
                'moyenne_min': 0,
                'pourcentage_reussite': 0,
                'nb_eleves_total': eleves.count(),
                'nb_eleves_admis': 0,
                'nb_eleves_ajournes': 0
            }
        
        nb_admis = len([m for m in moyennes if m >= 10])
        nb_ajournes = len([m for m in moyennes if m < 10])
        
        return {
            'moyenne_generale': round(sum(moyennes) / len(moyennes), 2),
            'moyenne_max': max(moyennes),
            'moyenne_min': min(moyennes),
            'pourcentage_reussite': round((nb_admis / len(moyennes)) * 100, 2),
            'nb_eleves_total': len(moyennes),
            'nb_eleves_admis': nb_admis,
            'nb_eleves_ajournes': nb_ajournes
        }
    
    @property
    def total_coffecient(self):
        return sum(item.coefficient for item in self.matiere_set.all())
    


    def __str__(self):
        return f'{self.libelle}({self.code})' 
    

class Eleve(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="eleve_profile")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="eleves")
    date_naissance = models.DateField(blank=True, null=True)
    lieu_naissance = models.CharField(max_length=255, default='douala')
    nom_pere = models.CharField(max_length=255)
    nom_mere = models.CharField(max_length=255)
    email_parent = models.EmailField()
    phone_parent = models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    sexe = models.CharField(max_length=50, choices=[
        ("Masculin", "Masculin"),
        ("Feminin", "Feminin"),
    ], default="Feminin")

    @property
    def moyenne(self):
        """
        Calcule la moyenne d'un élève pour une séquence donnée
        type_sequence: "1" ou "2"
        """
        type_sequence=1

        # Récupérer toutes les notes de l'élève pour cette séquence
        notes = self.notes.filter(
            evaluation__type_evaluation=type_sequence
        ).select_related('evaluation__matiere')
        
        if not notes.exists():
            return 0
        
        # Calculer le total pondéré et total des coefficients
        total = Decimal('0')
        total_coef = 0
        
        # Calculer le total pondéré (note * coefficient)
        total = sum([float(note.note) * note.evaluation.matiere.coefficient for note in notes])
        
        # Calculer la somme des coefficients
        total_coef = sum([note.evaluation.matiere.coefficient for note in notes])
        
        if total_coef == 0:
            return 0
            
        return round(total / total_coef, 2)
    
    def rang(self):
        type_sequence =1
        """
        Calcule le rang d'un élève dans sa classe pour une séquence donnée
        Retourne un tuple (rang, total_eleves)
        """
        # Récupérer tous les élèves de la même classe
        eleves_classe = self.classe.eleves.all()
        
        # Calculer les moyennes de tous les élèves
        moyennes = []
        for eleve in eleves_classe:
            moyenne = eleve.moyenne
            moyennes.append({
                'eleve_id': eleve.id,
                'moyenne': moyenne
            })
        
        # Trier par moyenne décroissante
        moyennes.sort(key=lambda x: x['moyenne'], reverse=True)

        # Trouver le rang de l'élève actuel
        rang = None
        for i, item in enumerate(moyennes, 1):
            if item['eleve_id'] == self.id:
                rang = i
                break
        
        return rang
    
    @property
    def mention(self):
        type_sequence=1
        """
        Retourne la mention selon la moyenne
        """
        moyenne = moyenne = Decimal(str(self.moyenne))

        if moyenne >= 19:
            return "Excellent"
        if moyenne >= 18:
            return "Excellent"
        elif moyenne >= 16:
            return "Très Bien"
        elif moyenne >= 14:
            return "Bien"
        elif moyenne >= 12:
            return "Assez bien"
        elif moyenne >= 10:
            return "Passable"
        elif moyenne >= 8:
            return "Mediocre"
        else:
            return "Insuffisant"
    
    @property
    def appreciation(self):
        type_sequence=1
        """
        Retourne une appréciation détaillée
        """
        moyenne = Decimal(str(self.moyenne))
        
        if moyenne >= 18:
            return "Excellent travail, continuez ainsi !"
        elif moyenne >= 16:
            return "Très bon travail"
        elif moyenne >= 14:
            return "Bon travail"
        elif moyenne >= 12:
            return "Travail satisfaisant"
        elif moyenne >= 10:
            return "Peut mieux faire"
        elif moyenne >= 8:
            return "Travail insuffisant, il faut se ressaisir"
        else:
            return "Travail très insuffisant, redoublez d'efforts"


    def __str__(self):
        return f"{self.user.get_full_name()}"


class Enseignant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="enseignant_profile")
    grade = models.CharField(max_length=100)
    matiere = models.CharField(max_length=100)  # ex: "Mathématiques"
    phone_number = models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    sexe = models.CharField(max_length=50, choices=[
        ("Masculin", "Masculin"),
        ("Feminin", "Feminin"),
    ], default="Feminin")


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

    @property
    def mention(self):
        type_sequence=1
        """
        Retourne la mention selon la moyenne
        """
        note = note = Decimal(str(self.note))

        if note >= 19:
            return "Excellent"
        if note >= 18:
            return "Excellent"
        elif note >= 16:
            return "Très Bien"
        elif note >= 14:
            return "Bien"
        elif note >= 12:
            return "Assez bien"
        elif note >= 10:
            return "Passable"
        elif note >= 8:
            return "Mediocre"
        else:
            return "Insuffisant"
    
    @property
    def rang(self):
        """
        Retourne le rang de cet élève dans sa classe pour cette évaluation
        """
        notes_classe = Note.objects.filter(
            eleve__classe=self.eleve.classe,
            evaluation=self.evaluation
        ).order_by('-note')
        
        if not notes_classe.exists():
            return None
        
        for i, note in enumerate(notes_classe, 1):
            if note.id == self.id:
                return i
        
        return None






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

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Eleve, Classe

class ClasseForm(forms.ModelForm):
    class Meta:
        model=Classe
        fields = ['libelle', 'code']
        labels = {
            'libelle':'Nom de la classe',
            'code':'Code la classe'
        }
        widgets ={
            'libelle':forms.TextInput(attrs={'class':'form-control'}),
            'code': forms.TextInput(attrs={'class':'form-control'}),
        }


from django.utils.crypto import get_random_string
import datetime
from .models import CustomUser, Eleve, Classe, Enseignant, Matiere

class EleveRegisterForm(forms.ModelForm):
    nom_pere = forms.CharField(
        label="Nom du père",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    lieu_naissance = forms.CharField(
        label="Lieu de naissance",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    nom_mere = forms.CharField(
        label="Nom de la mère",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email_parent = forms.EmailField(
        label="Email du parent",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_parent = forms.CharField(
        label="Téléphone du parent",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_naissance = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        label="Classe",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    sexe = forms.CharField(
    label="Sexe",
    widget=forms.Select(
        choices=[
            ('', 'Sélectionner'),  # Option vide par défaut
            ('Masculin', 'Masculin'),
            ('Féminin', 'Féminin'),
        ],
        attrs={'class': 'form-control'}
    )
)

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name")
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={'class': 'form-control'}),
            "last_name": forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # on ne fait pas super().save() pour éviter le bug UserCreationForm
        user = super().save(commit=False)
        user.role = "eleve"

        # ⚡ Génération matricule unique
        annee = datetime.date.today().year
        matricule = f"{annee}{get_random_string(6).upper()}"
        while CustomUser.objects.filter(username=matricule).exists():
            matricule = f"{annee}{get_random_string(6).upper()}"

        user.username = matricule
        user.matricule = matricule

        # ⚡ Génération mot de passe auto
        password = get_random_string(8)
        user.set_password(password)

        # ⚡ email = email du parent
        user.email = self.cleaned_data["email_parent"]

        if commit:
            user.save()
            Eleve.objects.create(
                user=user,
                classe=self.cleaned_data["classe"],
                date_naissance=self.cleaned_data["date_naissance"],
                nom_pere=self.cleaned_data["nom_pere"],
                nom_mere=self.cleaned_data["nom_mere"],
                email_parent=self.cleaned_data["email_parent"],
                phone_parent=self.cleaned_data["phone_parent"],
                lieu_naissance=self.cleaned_data["lieu_naissance"],
                sexe=self.cleaned_data["sexe"],
                password=password,

            )
        return user, matricule, password

class TeacherRegisterForm(forms.ModelForm):
    grade = forms.CharField(
        label="Grade",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    matiere = forms.CharField(
        label="Discipline",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sexe = forms.CharField(
    label="Sexe",
    widget=forms.Select(
        choices=[
            ('', 'Sélectionner'),  # Option vide par défaut
            ('Masculin', 'Masculin'),
            ('Féminin', 'Féminin'),
        ],
        attrs={'class': 'form-control'}
    )
)
    phone_number = forms.CharField(
        label="Téléphone du parent",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
 

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Adresse email"
        }
        widgets = {
            "first_name": forms.TextInput(attrs={'class': 'form-control'}),
            "last_name": forms.TextInput(attrs={'class': 'form-control'}),
            "email": forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        # on ne fait pas super().save() pour éviter le bug UserCreationForm
        user = super().save(commit=False)
        user.role = "enseignant"

        # ⚡ Génération matricule unique
        annee = datetime.date.today().year
        matricule = f"{annee}{get_random_string(6).upper()}"
        while CustomUser.objects.filter(username=matricule).exists():
            matricule = f"{annee}{get_random_string(6).upper()}"

        user.username = matricule
        user.matricule = matricule

        # ⚡ Génération mot de passe auto
        password = get_random_string(8)
        user.set_password(password)

        # ⚡ email = email du parent
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            Enseignant.objects.create(
                user=user,
                grade=self.cleaned_data["grade"],
                matiere=self.cleaned_data["matiere"],
                phone_number=self.cleaned_data["phone_number"],
                sexe=self.cleaned_data["sexe"],
                password=password,
            )
        return user, matricule, password

class MatiereRigisterForm(forms.ModelForm):
   class Meta:
        model=Matiere
        fields = ['nom', 'coefficient','enseignant','classe']
        labels = {
            'nom':'Libelle de la matiere',
            'coefficient':'Coefficient',
            'enseignant':'Enseignant',
            'classe':'Classe'
        }
        widgets ={
            'nom':forms.TextInput(attrs={'class':'form-control'}),
            'coefficient': forms.TextInput(attrs={'class':'form-control'}),
            'classe': forms.Select(attrs={'class':'form-control'}),
            'enseignant': forms.Select(attrs={'class':'form-control'}),
        }
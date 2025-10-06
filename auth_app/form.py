from django import forms
from .models import CustomUser as User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

class LoginForm(forms.Form):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Entrer votre mot de passe'}))
    matricule=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control",'placeholder':'Entre votre matricule'}))

    def clean(self):
        matricule = self.cleaned_data.get('matricule')
        password = self.cleaned_data.get('password')
        UserModel = get_user_model()
        
        if matricule and password:
            try:
                user = User.objects.get(matricule=matricule)
                if not user.check_password(password):
                    raise forms.ValidationError("Matricule ou mot de passe incorrect")
            except UserModel.DoesNotExist:
                raise forms.ValidationError("Matricule ou mot de passe incorrect")
        
        return self.cleaned_data
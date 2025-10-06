from django.shortcuts import render, redirect
from .form import *
from django.contrib import messages
from django.contrib.auth import get_user_model, login,logout


# Create your views here.
def connexion(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():   
           matricule = form.cleaned_data.get('matricule')
           password = form.cleaned_data.get('password')
           UserModel = get_user_model()
           try:
                user = UserModel.objects.get(matricule=matricule)
                if user.check_password(password):
                    if not user.is_active:
                        messages.error(request, "Votre compte est bloqué. Veuillez contacter l'administration.")
                    else:
                        login(request,user)
                        return redirect('index')  # Remplacez 'home' par le nom de l'URL de votre page d'accueil
                else:  
                    messages.error(request, 'matricule ou mot de passe incorrect.')
           except UserModel.DoesNotExist:
                messages.error(request, 'matricule ou mot de passe incorrect.')    
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form':form})

def logoutPage(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('login')

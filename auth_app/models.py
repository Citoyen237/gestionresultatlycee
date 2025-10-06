from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from admin_site.models import *
# from usesOrders.models import Order
# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("eleve", "Élève"),
        ("enseignant", "Enseignant"),
        ("admin", "Administrateur"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='eleve')
    matricule = models.CharField(max_length=50, unique=True)


    def is_eleve(self):
        return self.role == "eleve"

    def is_enseignant(self):
        return self.role == "enseignant"

    def __str__(self):
        return f"{self.username}"

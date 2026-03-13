from django.db import models
from django.contrib.auth.models import AbstractUser
from store.domain.code_generator import generate_code

# =========================
# UTILISATEUR
# =========================
class Utilisateur(AbstractUser):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    role = models.CharField(
        max_length=30,
        choices=[
            ("admin", "Admin"),
            ("client", "Client"),
            ("livreur", "Livreur"),
        ],
        default="client",
    )
    statut = models.CharField(max_length=10, 
        choices=[
            ("actif", "Actif"),
            ("desactive", "Desactive"),
            ("suprime", "Suprime"),
        ],
        default="actif",
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("UTIL")
        super().save(*args, **kwargs)

# =========================
# CLIENT
# =========================
class Client(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="profil_client",
    )
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("CLIE")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

# =========================
# LIVREUR
# =========================
class Livreur(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="profil_livreur",
    )
    telephone = models.CharField(max_length=20)
    moyen_transport = models.CharField(max_length=30)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("LIVR")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.utilisateur.username

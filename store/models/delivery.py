# store/models/delivery.py
from django.db import models
from store.domain.code_generator import generate_code
from accounts.models import Livreur


class Livraison(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)

    livreur = models.ForeignKey(
        Livreur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="livraisons"
    )

    date_livraison = models.DateTimeField(null=True, blank=True)

    etat = models.CharField(
        max_length=30,
        choices=[
            ("EN_ATTENTE", "En attente"),
            ("EN_COURS", "En cours"),
            ("LIVREE", "Livrée"),
            ("ANNULEE", "Annulée"),
        ],
        default="EN_ATTENTE"
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("LIVS")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Livraison {self.id}"

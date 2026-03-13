from django.db import models
from django.conf import settings
from store.domain.code_generator import generate_code
from store.models.cart import Panier


class Paiement(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paiements"
    )
    panier = models.OneToOneField(
        Panier,
        on_delete=models.PROTECT,
        related_name="paiement"
    )
    date_paiement = models.DateTimeField(auto_now_add=True)
    mode_paiement = models.CharField(max_length=30)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(
        max_length=20,
        choices=[
            ("EN_ATTENTE", "En attente"),
            ("VALIDE", "Validé"),
            ("ECHEC", "Échec"),
        ],
        default="EN_ATTENTE"
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("PAIE")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Paiement {self.id}"

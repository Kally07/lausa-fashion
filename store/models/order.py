# store/models/order.py
from django.db import models
from django.conf import settings
from store.domain.code_generator import generate_code
from store.models.delivery import Livraison
from store.models.payment import Paiement
from store.models.product import Produit


class Commande(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commandes"
    )

    paiement = models.OneToOneField(
        Paiement,
        on_delete=models.PROTECT,
        related_name="commande"
    )

    livraison = models.ForeignKey(
        Livraison,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commandes"
    )

    date_commande = models.DateTimeField(auto_now_add=True)
    date_livraison = models.DateTimeField()

    statut = models.CharField(
        max_length=20,
        choices=[
            ("EN_PREPARATION", "En préparation"),
            ("EXPEDIEE", "Expédiée"),
            ("LIVREE", "Livrée"),
            ("ANNULEE", "Annulée"),
        ],
        default="EN_PREPARATION"
    )

    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("COMM")
        super().save(*args, **kwargs)

    @property
    def total(self):
        return sum(ligne.total for ligne in self.lignes.all())

    def __str__(self):
        return f"Commande {self.id}"

class LigneCommande(models.Model):
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name="lignes"
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,
        related_name="lignes_commande"
    )
    quantite = models.PositiveIntegerField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.prix * self.quantite

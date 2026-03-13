from django.db import models
from django.conf import settings
from store.domain.code_generator import generate_code
from store.models.product import Produit


class Panier(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paniers"
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("PANI")
        super().save(*args, **kwargs)

    @property
    def total(self):
        return sum(item.total for item in self.items.all())

    def __str__(self):
        return f"Panier {self.id}"


class PanierItem(models.Model):
    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name="items"
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name="panier_items"
    )
    quantite = models.PositiveIntegerField(default=1)

    @property
    def total(self):
        return self.produit.prix * self.quantite

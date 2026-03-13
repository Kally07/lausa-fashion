from django.db import models
from store.domain.code_generator import generate_code


# =========================
# CATEGORIE
# =========================
class Categorie(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("CATG")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


# =========================
# SOUS-CATEGORIE
# =========================
class SousCategorie(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        related_name="sous_categories"
    )

    class Meta:
        unique_together = ("nom",)
        verbose_name = "Sous-catégorie"
        verbose_name_plural = "Sous-catégories"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("SCAT")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.categorie.nom} - {self.nom}"


# =========================
# PRODUIT
# =========================
class Produit(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="produits/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    sous_categorie = models.ForeignKey(
        SousCategorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produits"
    )

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("PROD")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom
from django.core.exceptions import ValidationError

class Produit(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="produits/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    sous_categorie = models.ForeignKey(
        SousCategorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produits"
    )

    def clean(self):
        if self.prix < 0:
            raise ValidationError("Le prix ne peut pas être négatif.")
        if self.stock < 0:
            raise ValidationError("Le stock ne peut pas être négatif.")

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_code("PROD")
        self.full_clean()  # valide avant d'enregistrer
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

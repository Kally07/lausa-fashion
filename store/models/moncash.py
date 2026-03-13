from django.db import models

class MonCash(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    motpass = models.CharField(max_length=4)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.numero} - {self.montant} HTG"

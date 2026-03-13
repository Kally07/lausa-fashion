from django.db.models import F, Sum
from store.models.order import LigneCommande

def calculer_total_commande(commande):
    total = (
        LigneCommande.objects
        .filter(commande=commande)
        .aggregate(
            total=Sum(F("quantite") * F("produit__prix"))
        )["total"]
    ) or 0

    return float(total)

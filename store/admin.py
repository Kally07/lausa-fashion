from django.contrib import admin

# Register your models here.
from .models import Sequence, MonCash, Categorie, SousCategorie, Produit, Commande, LigneCommande, Panier, PanierItem, Paiement, Livraison, Historique

admin.site.register(Produit)
admin.site.register(Categorie)
admin.site.register(SousCategorie)
admin.site.register(Commande)
admin.site.register(LigneCommande)
admin.site.register(Panier)
admin.site.register(PanierItem)
admin.site.register(Paiement)
admin.site.register(Livraison)
admin.site.register(Historique)
admin.site.register(MonCash)
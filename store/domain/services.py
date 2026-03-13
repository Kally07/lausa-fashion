from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import Sum, Q

from store.models.cart import Panier, PanierItem
from store.models.order import Commande, LigneCommande
from store.models.product import Produit, Categorie
from store.models.payment import Paiement
from store.models.history import Historique

from store.domain.paiement_moncash import valider_paiement_moncash
from store.domain.paiement_natcash import valider_paiement_natcash

from store.domain.exceptions import (
    PaiementInvalideError,
    AccesInterditError,
    PanierVideError,
    StockInsuffisantError
)

# =====================================================
# HISTORIQUE
# =====================================================

def enregistrer_action(utilisateur: User, action: str):
    Historique.objects.create(
        utilisateur=utilisateur,
        action=action
    )

# =====================================================
# PANIER
# =====================================================

def obtenir_panier_actif(user: User) -> Panier:
    panier, _ = Panier.objects.get_or_create(
        user=user,
        actif=True
    )
    return panier


def ajouter_produit_au_panier(user: User, produit: Produit, quantite: int):
    if quantite <= 0:
        raise ValueError("Quantité invalide")

    panier = obtenir_panier_actif(user)

    item, created = PanierItem.objects.get_or_create(
        panier=panier,
        produit=produit
    )

    quantite_totale = quantite if created else item.quantite + quantite

    if quantite_totale > produit.stock:
        raise StockInsuffisantError(
            f"Stock insuffisant (disponible : {produit.stock})"
        )

    item.quantite = quantite_totale
    item.save()

    return item


def modifier_quantite_panier(user: User, item_id: int, action: str):
    panier = obtenir_panier_actif(user)

    item = PanierItem.objects.get(
        id=item_id,
        panier=panier
    )

    if action == "plus":
        if item.quantite + 1 > item.produit.stock:
            raise StockInsuffisantError("Stock insuffisant")
        item.quantite += 1
        item.save()
        return item

    if action == "moins":
        item.quantite -= 1
        if item.quantite <= 0:
            item.delete()
            return None
        item.save()
        return item

    raise ValueError("Action invalide")


def supprimer_item_panier(user: User, item_id: int):
    panier = obtenir_panier_actif(user)
    PanierItem.objects.filter(
        id=item_id,
        panier=panier
    ).delete()


def vider_panier(user: User):
    panier = obtenir_panier_actif(user)
    panier.items.all().delete()


def obtenir_panier(user: User):
    panier = obtenir_panier_actif(user)
    items = panier.items.select_related("produit")
    return items, panier.total


def get_panier_count(user: User) -> int:
    if not user.is_authenticated:
        return 0

    panier = Panier.objects.filter(user=user, actif=True).first()
    if not panier:
        return 0

    return (
        panier.items
        .aggregate(total=Sum("quantite"))["total"]
        or 0
    )

# =====================================================
# COMMANDE & PAIEMENT
# =====================================================

def payer_panier(
    user: User,
    mode_paiement: str,
    reference: str = None,
    adresse: str = "",
    telephone: str = "",
    date_livraison: str = None
):
    panier = obtenir_panier_actif(user)
    items = panier.items.select_related("produit")

    if not items.exists():
        raise PanierVideError("Le panier est vide")

    total = panier.total

    # Validation paiement
    if mode_paiement == "MonCash":
        pass
    elif mode_paiement == "NatCash":
        valider_paiement_natcash(reference, total)
    elif mode_paiement not in ["Cash", "Carte"]:
        raise PaiementInvalideError("Mode de paiement invalide")

    with transaction.atomic():

        # Vérification & réservation du stock
        for item in items:
            produit = Produit.objects.select_for_update().get(pk=item.produit.pk)
            if item.quantite > produit.stock:
                raise StockInsuffisantError(
                    f"Stock insuffisant pour {produit.nom}"
                )

        # Paiement
        paiement = Paiement.objects.create(
            user=user,
            panier=panier,
            mode_paiement=mode_paiement,
            montant_total=total,
            statut="VALIDE"
        )

        # Commande
        commande = Commande.objects.create(
            user=user,
            paiement=paiement,
            adresse=adresse,
            telephone=telephone,
            statut="EN_PREPARATION",
            date_livraison=date_livraison
        )

        # Lignes + déduction stock
        for item in items:
            produit = Produit.objects.select_for_update().get(pk=item.produit.pk)

            LigneCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=item.quantite,
                prix=produit.prix
            )

            produit.stock -= item.quantite
            produit.save()

        panier.actif = False
        panier.save()

        enregistrer_action(
            user,
            f"Paiement {paiement.id} – Commande {commande.id}"
        )

    return commande, paiement


def annuler_commande(user: User, commande: Commande):
    if commande.user != user:
        raise AccesInterditError("Accès interdit")

    if commande.statut == "ANNULEE":
        raise PaiementInvalideError("Commande déjà annulée")

    with transaction.atomic():
        for ligne in commande.lignes.select_related("produit"):
            produit = Produit.objects.select_for_update().get(
                pk=ligne.produit.pk
            )
            produit.stock += ligne.quantite
            produit.save()

        commande.statut = "ANNULEE"
        commande.save()

        enregistrer_action(
            user,
            f"Annulation commande {commande.id}"
        )

    return commande

# =====================================================
# PRODUITS / RECHERCHE
# =====================================================

from django.db.models import Q
from store.models import Produit

def rechercher_produits(user=None, mot_clef: str = ""):
    # Aucun mot-clé -> retourne un QuerySet vide
    if not mot_clef.strip():
        return Produit.objects.none()

    # Log de l'action si l'utilisateur est fourni
    if user:
        enregistrer_action(user, f"Recherche de produits avec le mot-clé '{mot_clef}'")

    # Filtre les produits par nom ou description (case-insensitive)
    return Produit.objects.filter(
        Q(nom__icontains=mot_clef) |
        Q(description__icontains=mot_clef)
    )


def produits_par_categorie(categorie: Categorie):
    return Produit.objects.filter(
        sous_categorie__categories=categorie
    ).distinct()


from store.models.moncash import MonCash
from django.db import transaction
from decimal import Decimal

def traiter_paiement_moncash_local(user, numero, motpass):

    with transaction.atomic():

        panier = obtenir_panier_actif(user)
        total = panier.total

        try:
            compte = MonCash.objects.select_for_update().get(
                numero=numero,
                motpass=motpass
            )
        except MonCash.DoesNotExist:
            raise PaiementInvalideError("Numéro ou mot de passe incorrect.")

        if compte.montant < total:
            raise PaiementInvalideError("Solde insuffisant.")

        compte.montant -= Decimal(total)
        compte.save()

    return True
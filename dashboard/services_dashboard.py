# dashboard/services/services_dashboard.py

from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from accounts.services_accounts import verifier_acces_admin
from accounts.models import Client, Livreur

from store.models.product import Produit, Categorie, SousCategorie
from store.models.order import Commande, LigneCommande
from store.models.delivery import Livraison
from store.models.payment import Paiement
from store.domain.services import enregistrer_action


Utilisateur = get_user_model()

# =====================================================
# PRODUITS
# =====================================================

def creer_produit(user, **data):
    verifier_acces_admin(user)

    prix = float(data.get("prix", 0))
    stock = int(data.get("stock", 0))

    if prix < 0 or stock < 0:
        raise ValueError("Prix et stock doivent être positifs.")

    produit = Produit.objects.create(**data)
    enregistrer_action(user, f"Création produit #{produit.id}")
    return produit

def creer_ou_maj_produit(user, nom, prix=0, stock=0, description="", sous_categorie=None, image=None):
    """
    Si un produit avec le même nom existe déjà, ajoute le stock.
    Sinon, crée un nouveau produit.
    """
    verifier_acces_admin(user)

    # Validation
    try:
        prix = float(prix)
        stock = int(stock)
    except ValueError:
        raise ValidationError("Prix et stock doivent être numériques.")
    
    if prix < 0 or stock < 0:
        raise ValidationError("Prix et stock doivent être positifs.")

    # Chercher produit existant
    produit = Produit.objects.filter(nom__iexact=nom).first()

    if produit:
        # Ajouter au stock existant
        produit.stock += stock
        if prix != produit.prix:
            produit.prix = prix  # On peut décider si on met à jour le prix
        produit.save()
        action = f"Ajout de {stock} au stock du produit existant #{produit.id}"
    else:
        # Créer un nouveau produit
        produit = Produit.objects.create(
            nom=nom,
            prix=prix,
            stock=stock,
            description=description,
            sous_categorie=sous_categorie,
            image=image
        )
        action = f"Création nouveau produit #{produit.id}"

    enregistrer_action(user, action)
    return produit

def modifier_produit(user, produit: Produit, **data):
    verifier_acces_admin(user)

    for champ, valeur in data.items():
        setattr(produit, champ, valeur)

    produit.save()
    enregistrer_action(user, f"Modification produit #{produit.id}")
    return produit


def supprimer_produit(user, produit: Produit):
    verifier_acces_admin(user)
    nom = produit.nom
    produit.delete()
    enregistrer_action(user, f"Suppression produit {nom}")


def lister_produits(
    user,
    query=None,
    categorie_id=None,
    sous_categorie_id=None
):
    verifier_acces_admin(user)

    produits = Produit.objects.select_related("sous_categorie__categorie")

    if query:
        produits = produits.filter(
            Q(nom__icontains=query) |
            Q(description__icontains=query)
        )

    if categorie_id:
        produits = produits.filter(
            sous_categorie__categories__id=categorie_id
        )

    if sous_categorie_id:
        produits = produits.filter(
            sous_categorie_id=sous_categorie_id
        )

    enregistrer_action(user, "Consultation liste produits")

    return produits.distinct()

# =====================================================
# CATEGORIES
# =====================================================

def creer_categorie(user, nom, description=""):
    verifier_acces_admin(user)
    categorie = Categorie.objects.create(nom=nom, description=description)
    enregistrer_action(user, f"Création catégorie {nom}")
    return categorie


def modifier_categorie(user, categorie: Categorie, **data):
    verifier_acces_admin(user)

    for champ, valeur in data.items():
        setattr(categorie, champ, valeur)

    categorie.save()
    enregistrer_action(user, f"Modification catégorie {categorie.nom}")
    return categorie


def supprimer_categorie(user, categorie: Categorie):
    verifier_acces_admin(user)
    nom = categorie.nom
    categorie.delete()
    enregistrer_action(user, f"Suppression catégorie {nom}")


def lister_categories(user):
    verifier_acces_admin(user)
    enregistrer_action(user, "Consultation liste catégories")
    return Categorie.objects.all()

# =====================================================
# SOUS-CATEGORIES
# =====================================================

def creer_sous_categorie(user, categorie_id, nom, description=""):
    verifier_acces_admin(user)

    if not categorie_id:
        raise ValueError("La catégorie est obligatoire.")

    categorie = get_object_or_404(Categorie, id=categorie_id)

    sous_categorie = SousCategorie.objects.create(
        categorie=categorie,  # correspond maintenant au champ correct
        nom=nom,
        description=description
    )

    enregistrer_action(user, f"Création sous-catégorie {nom}")
    return sous_categorie




def modifier_sous_categorie(user, sous_categorie: SousCategorie, **data):
    verifier_acces_admin(user)

    for champ, valeur in data.items():
        setattr(sous_categorie, champ, valeur)

    sous_categorie.save()
    enregistrer_action(user, f"Modification catégorie {sous_categorie.nom}")
    return sous_categorie


def supprimer_sous_categorie(user, sous_categorie: SousCategorie):
    verifier_acces_admin(user)
    nom = sous_categorie.nom
    sous_categorie.delete()
    enregistrer_action(user, f"Suppression catégorie {nom}")


def lister_sous_categories(user, categorie_id=None):
    verifier_acces_admin(user)

    qs = SousCategorie.objects.all()

    if categorie_id:
        qs = qs.filter(categories__id=categorie_id)

    return qs.distinct()

def sous_categories_par_categorie(categorie_id):
    return SousCategorie.objects.filter(
        categories__id=categorie_id
    ).distinct()
# =====================================================
# COMMANDES
# =====================================================

@transaction.atomic
def creer_commande(user, client, lignes, adresse=None, telephone=None):
    verifier_acces_admin(user)

    commande = Commande.objects.create(
        user=client,
        adresse=adresse,
        telephone=telephone,
        statut="EN_ATTENTE"
    )

    for ligne in lignes:
        LigneCommande.objects.create(
            commande=commande,
            produit=ligne["produit"],
            quantite=ligne["quantite"],
            prix=ligne["produit"].prix
        )

    enregistrer_action(user, f"Création commande #{commande.id}")
    return commande


def modifier_commande(user, commande: Commande, **data):
    verifier_acces_admin(user)

    for champ, valeur in data.items():
        setattr(commande, champ, valeur)

    commande.save()
    enregistrer_action(user, f"Modification commande #{commande.id}")
    return commande


def valider_commande(user, commande: Commande):
    verifier_acces_admin(user)
    commande.statut = "VALIDE"
    commande.save()
    enregistrer_action(user, f"Validation commande #{commande.id}")


def annuler_commande(user, commande: Commande, motif=""):
    verifier_acces_admin(user)
    commande.statut = "ANNULEE"
    commande.motif_annulation = motif
    commande.save()
    enregistrer_action(user, f"Annulation commande #{commande.id}")


def supprimer_commande(user, commande: Commande):
    verifier_acces_admin(user)
    cid = commande.id
    commande.delete()
    enregistrer_action(user, f"Suppression commande #{cid}")


def liste_commandes(user):
    verifier_acces_admin(user)
    enregistrer_action(user, "Consultation liste commandes")
    return Commande.objects.all().order_by("-date_commande")


def rechercher_commandes(user, query):
    verifier_acces_admin(user)
    enregistrer_action(user, f"Recherche commandes : {query}")
    return Commande.objects.filter(
        Q(id__icontains=query) |
        Q(user__username__icontains=query) |
        Q(statut__icontains=query)
    )

def liste_commandes_par_statut(user, statut):
    verifier_acces_admin(user)
    return Commande.objects.filter(statut=statut).order_by("-date_commande")


# =====================================================
# LIVRAISONS
# =====================================================

@transaction.atomic
def creer_livraison(user, livreur: Livreur, commandes):
    verifier_acces_admin(user)

    # Création de la livraison
    livraison = Livraison.objects.create(
        livreur=livreur,
        date_livraison=timezone.now(),
        etat="EN_COURS"
    )

    # Associer les commandes à la livraison + changer leur statut
    commandes.update(
        livraison=livraison,
        statut="EXPEDIEE"
    )

    enregistrer_action(
        user,
        f"Création livraison #{livraison.id} - {commandes.count()} commandes expédiées"
    )

    return livraison


def terminer_livraison(user, livraison: Livraison):
    verifier_acces_admin(user)
    livraison.etat = "TERMINEE"
    livraison.save()
    enregistrer_action(user, f"Livraison #{livraison.id} terminée")


def lister_livraisons(user):
    verifier_acces_admin(user)
    enregistrer_action(user, "Consultation liste livraisons")
    return Livraison.objects.all().order_by("-date_livraison")


# =====================================================
# PAIEMENTS
# =====================================================

def lister_paiements(user):
    verifier_acces_admin(user)
    enregistrer_action(user, "Consultation liste paiements")
    return Paiement.objects.all().order_by("-date_paiement")

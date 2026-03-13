from django.shortcuts import redirect
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import PermissionDenied, ValidationError

from accounts.models import Utilisateur, Client, Livreur
from store.domain.services import enregistrer_action


# =====================================================
# VÉRIFICATIONS D’ACCÈS
# =====================================================

def verifier_acces_admin(utilisateur: Utilisateur):
    if not utilisateur or not utilisateur.is_authenticated:
        raise PermissionDenied("Utilisateur non authentifié.")
    if utilisateur.role != "admin":
        raise PermissionDenied("Accès réservé aux administrateurs.")


def verifier_acces_livreur(utilisateur: Utilisateur):
    if not utilisateur or not utilisateur.is_authenticated:
        raise PermissionDenied("Utilisateur non authentifié.")
    if utilisateur.role != "livreur":
        raise PermissionDenied("Accès réservé aux livreurs.")


# =====================================================
# UTILISATEURS (ADMIN)
# =====================================================

@transaction.atomic
def creer_utilisateur(
    admin: Utilisateur,
    username: str,
    email: str,
    password: str,
    role: str = "client",
    actif: bool = True
) -> Utilisateur:
    """
    Création d'un utilisateur par un admin
    """
    verifier_acces_admin(admin)

    if Utilisateur.objects.filter(username=username).exists():
        raise ValidationError("Nom d'utilisateur déjà utilisé")

    utilisateur = Utilisateur.objects.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
        statut="actif" if actif else "desactive",
        is_active=actif
    )

    enregistrer_action(admin, f"Création utilisateur {username}")
    return utilisateur


def modifier_utilisateur(admin: Utilisateur, utilisateur: Utilisateur, **data):
    verifier_acces_admin(admin)

    for champ, valeur in data.items():
        if champ == "password":
            utilisateur.set_password(valeur)
        elif hasattr(utilisateur, champ):
            setattr(utilisateur, champ, valeur)

    utilisateur.save()
    enregistrer_action(admin, f"Modification utilisateur {utilisateur.username}")
    return utilisateur


def activer_utilisateur(admin: Utilisateur, utilisateur: Utilisateur):
    verifier_acces_admin(admin)
    utilisateur.statut = "actif"
    utilisateur.is_active = True
    utilisateur.save(update_fields=["statut", "is_active"])
    enregistrer_action(admin, f"Activation utilisateur {utilisateur.username}")


def desactiver_utilisateur(admin: Utilisateur, utilisateur: Utilisateur):
    verifier_acces_admin(admin)
    utilisateur.statut = "desactive"
    utilisateur.is_active = False
    utilisateur.save(update_fields=["statut", "is_active"])
    enregistrer_action(admin, f"Désactivation utilisateur {utilisateur.username}")


def supprimer_utilisateur(admin: Utilisateur, utilisateur: Utilisateur):
    verifier_acces_admin(admin)

    if admin == utilisateur:
        raise ValidationError("Impossible de supprimer son propre compte")

    utilisateur.statut = "suprime"   # ⚠️ aligné avec models.py
    utilisateur.is_active = False
    utilisateur.save(update_fields=["statut", "is_active"])

    enregistrer_action(admin, f"Suppression utilisateur {utilisateur.username}")


def lister_utilisateurs(admin: Utilisateur):
    verifier_acces_admin(admin)
    enregistrer_action(admin, "Consultation liste utilisateurs")
    return Utilisateur.objects.exclude(statut="suprime").order_by("-date_joined")


def rechercher_utilisateurs(admin: Utilisateur, query: str):
    verifier_acces_admin(admin)
    enregistrer_action(admin, f"Recherche utilisateur : {query}")
    return Utilisateur.objects.exclude(statut="suprime").filter(
        Q(username__icontains=query) |
        Q(email__icontains=query)
    )


# =====================================================
# CLIENTS
# =====================================================

@transaction.atomic
def creer_client(
    admin: Utilisateur,
    username: str,
    password: str,
    email: str,
    nom: str,
    prenom: str,
    telephone: str = "",
    adresse: str = ""
) -> Client:
    utilisateur = creer_utilisateur(
        admin=admin,
        username=username,
        email=email,
        password=password,
        role="client",
        actif=True
    )

    client = Client.objects.create(
        utilisateur=utilisateur,
        nom=nom,
        prenom=prenom,
        telephone=telephone,
        adresse=adresse
    )

    enregistrer_action(admin, f"Création client {username}")
    return client


def modifier_client(admin: Utilisateur, client: Client, **data):
    verifier_acces_admin(admin)

    for champ, valeur in data.items():
        if hasattr(client, champ):
            setattr(client, champ, valeur)

    client.save()
    enregistrer_action(admin, f"Modification client {client.utilisateur.username}")
    return client


def supprimer_client(admin: Utilisateur, client: Client):
    verifier_acces_admin(admin)

    utilisateur = client.utilisateur
    utilisateur.statut = "suprime"
    utilisateur.is_active = False
    utilisateur.save(update_fields=["statut", "is_active"])

    enregistrer_action(admin, f"Suppression client {utilisateur.username}")


def lister_clients(admin: Utilisateur):
    verifier_acces_admin(admin)
    enregistrer_action(admin, "Consultation liste clients")
    return Client.objects.select_related("utilisateur").exclude(
        utilisateur__statut="suprime"
    )


# =====================================================
# LIVREURS
# =====================================================

@transaction.atomic
def creer_livreur(
    admin: Utilisateur,
    username: str,
    password: str,
    email: str,
    telephone: str,
    moyen_transport: str
) -> Livreur:
    utilisateur = creer_utilisateur(
        admin=admin,
        username=username,
        email=email,
        password=password,
        role="livreur",
        actif=True
    )
    livreur = Livreur.objects.create(
        utilisateur=utilisateur,
        telephone=telephone,
        moyen_transport=moyen_transport
    )
    enregistrer_action(admin, f"Création livreur {username}")
    return livreur


def modifier_livreur(admin: Utilisateur, livreur: Livreur, **data):
    verifier_acces_admin(admin)

    for champ, valeur in data.items():
        if hasattr(livreur, champ):
            setattr(livreur, champ, valeur)

    livreur.save()
    enregistrer_action(admin, f"Modification livreur {livreur.utilisateur.username}")
    return livreur


def supprimer_livreur(admin: Utilisateur, livreur: Livreur):
    verifier_acces_admin(admin)

    utilisateur = livreur.utilisateur
    utilisateur.statut = "suprime"
    utilisateur.is_active = False
    utilisateur.save(update_fields=["statut", "is_active"])

    enregistrer_action(admin, f"Suppression livreur {utilisateur.username}")


def lister_livreurs(admin: Utilisateur):
    verifier_acces_admin(admin)
    enregistrer_action(admin, "Consultation liste livreurs")
    return Livreur.objects.select_related("utilisateur").exclude(
        utilisateur__statut="suprime"
    )


# =====================================================
# INSCRIPTION PUBLIQUE
# =====================================================

@transaction.atomic
def inscription_utilisateur(
    username: str,
    password: str,
    email: str = ""
) -> Utilisateur:
    """
    Inscription publique (client par défaut)
    """
    if Utilisateur.objects.filter(username=username).exists():
        raise ValidationError("Nom d'utilisateur déjà utilisé")

    utilisateur = Utilisateur.objects.create_user(
        username=username,
        password=password,
        email=email,
        role="client",
        statut="actif",
        is_active=True
    )

    enregistrer_action(utilisateur, f"Inscription utilisateur {username}")
    return utilisateur


@transaction.atomic
def devenir_client(
    utilisateur: Utilisateur,
    nom: str,
    prenom: str,
    telephone: str = "",
    adresse: str = ""
) -> Client:
    """
    Transformer un utilisateur existant en client
    """
    if not utilisateur.is_authenticated:
        raise ValidationError("Utilisateur non authentifié")

    if utilisateur.statut != "actif":
        raise ValidationError("Compte utilisateur inactif")

    if hasattr(utilisateur, "profil_client"):
        raise ValidationError("Cet utilisateur est déjà client")

    utilisateur.role = "client"
    utilisateur.save(update_fields=["role"])

    client = Client.objects.create(
        utilisateur=utilisateur,
        nom=nom,
        prenom=prenom,
        telephone=telephone,
        adresse=adresse
    )

    enregistrer_action(utilisateur, f"Création profil client {utilisateur.username}")
    return client


# =====================================================
# REDIRECTION APRÈS CONNEXION
# =====================================================

def rediriger_apres_connexion(utilisateur: Utilisateur):

    # Vérifier que le compte est actif
    if utilisateur.statut != "actif":
        return redirect("accounts:login")

    # Redirection selon le rôle
    if utilisateur.role == "admin":
        return redirect("dashboard:index")

    elif utilisateur.role == "livreur":
        return redirect("livreur:index")

    elif utilisateur.role == "client":
        return redirect("store:index")

    # Sécurité si rôle inconnu
    return redirect("store:index")

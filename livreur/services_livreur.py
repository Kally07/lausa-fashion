# livreur/services_livreur.py

from django.utils import timezone
# livreur/services_livreur.py

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from store.models.delivery import Livraison
from store.models.order import Commande
from store.domain.services import enregistrer_action


# =====================================================
# Vérification rôle
# =====================================================

def verifier_livreur(user):
    if user.role != "livreur":
        raise PermissionDenied("Accès réservé aux livreurs")


# =====================================================
# Dashboard
# =====================================================

def get_dashboard_data(user):
    verifier_livreur(user)

    livraisons = Livraison.objects.filter(
        livreur__utilisateur=user
    )

    data = {
        "total": livraisons.count(),
        "en_attente": livraisons.filter(etat="EN_ATTENTE").count(),
        "en_cours": livraisons.filter(etat="EN_COURS").count(),
        "livrees": livraisons.filter(etat="LIVREE").count(),
    }

    enregistrer_action(user, "Consultation dashboard livreur")

    return data


# =====================================================
# Liste des livraisons
# =====================================================

from django.db.models import Case, When, Value, IntegerField

def get_livraisons_livreur(user):
    verifier_livreur(user)

    livraisons = (
        Livraison.objects
        .filter(livreur__utilisateur=user)
        .select_related("livreur")
        .annotate(
            ordre_priorite=Case(
                When(etat="EN_COURS", then=Value(0)),
                When(etat="EN_ATTENTE", then=Value(1)),
                When(etat="LIVREE", then=Value(2)),
                When(etat="ANNULEE", then=Value(3)),
                default=Value(4),
                output_field=IntegerField()
            )
        )
        .order_by("ordre_priorite", "-date_livraison")
    )

    enregistrer_action(user, "Consultation liste livraisons")

    return livraisons

# =====================================================
# Détail livraison
# =====================================================

def get_livraison_detail(user, livraison_id):
    verifier_livreur(user)

    livraison = get_object_or_404(
        Livraison,
        id=livraison_id,
        livreur__utilisateur=user
    )

    commandes = livraison.commandes.all()

    enregistrer_action(user, f"Consultation livraison {livraison.id}")

    return livraison, commandes


# =====================================================
# Mise à jour statut livraison + commande
# =====================================================

def mettre_a_jour_statut_livraison(user, livraison_id, nouveau_statut):
    verifier_livreur(user)

    livraison = get_object_or_404(
        Livraison,
        id=livraison_id,
        livreur__utilisateur=user
    )

    livraison.etat = nouveau_statut

    if nouveau_statut == "LIVREE":
        livraison.date_livraison = timezone.now()

    livraison.save()

    # Synchronisation commande
    mapping = {
        "EN_COURS": "EXPEDIEE",
        "LIVREE": "LIVREE",
        "ANNULEE": "ANNULEE",
    }

    if nouveau_statut in mapping:
        for commande in livraison.commandes.all():
            commande.statut = mapping[nouveau_statut]
            commande.save()

    enregistrer_action(
        user,
        f"Modification statut livraison {livraison.id} → {nouveau_statut}"
    )

    return livraison


def obtenir_livraisons_du_livreur(user):
    """
    Retourne uniquement les livraisons du livreur connecté
    """

    if user.role != "livreur":
        raise PermissionDenied("Accès non autorisé")

    livraisons = Livraison.objects.filter(
        livreur__utilisateur=user
    ).select_related("livreur")

    enregistrer_action(user, "Consultation liste livraisons")

    return livraisons

def obtenir_detail_livraison(user, livraison_id):
    """
    Retourne une livraison spécifique si elle appartient au livreur
    """

    livraison = get_object_or_404(
        Livraison,
        id=livraison_id,
        livreur__utilisateur=user
    )

    enregistrer_action(user, f"Consultation livraison {livraison.id}")

    return livraison
def modifier_statut_livraison(user, livraison_id, nouveau_statut):
    """
    Permet au livreur de modifier le statut de sa livraison
    """

    livraison = get_object_or_404(
        Livraison,
        id=livraison_id,
        livreur__utilisateur=user
    )

    livraison.etat = nouveau_statut

    # Si livrée → enregistrer date
    if nouveau_statut == "LIVREE":
        livraison.date_livraison = timezone.now()

    livraison.save()

    enregistrer_action(
        user,
        f"Modification statut livraison {livraison.id} → {nouveau_statut}"
    )

    return livraison

def modifier_statut_commande_depuis_livraison(user, livraison_id, nouveau_statut):
    """
    Modifie le statut de la commande liée à la livraison
    """

    livraison = get_object_or_404(
        Livraison,
        id=livraison_id,
        livreur__utilisateur=user
    )

    commandes = livraison.commandes.all()

    for commande in commandes:
        commande.statut = nouveau_statut
        commande.save()

        enregistrer_action(
            user,
            f"Modification statut commande {commande.id} → {nouveau_statut}"
        )

    return commandes

from django.core.mail import send_mail
from django.conf import settings
from django.utils.dateparse import parse_datetime

def traiter_action_livraison(user, livraison_id, action, motif=None, nouvelle_date=None):

    verifier_livreur(user)

    livraison = get_object_or_404(
        Livraison,
        id=livraison_id,
        livreur__utilisateur=user
    )

    commandes = livraison.commandes.all()

    if action == "LIVREE":
        livraison.etat = "LIVREE"
        livraison.date_livraison = timezone.now()

        for commande in commandes:
            commande.statut = "LIVREE"
            commande.save()

        message_client = "Votre commande a été livrée avec succès."

    elif action == "ANNULEE":
        livraison.etat = "ANNULEE"
        livraison.motif_annulation = motif

        for commande in commandes:
            commande.statut = "ANNULEE"
            commande.save()

        message_client = f"Votre livraison a été annulée.\nMotif : {motif}"

    elif action == "REPORTER":
        nouvelle_date = parse_datetime(nouvelle_date)

        livraison.date_reportee = nouvelle_date
        livraison.date_livraison = nouvelle_date
        livraison.etat = "EN_ATTENTE"

        message_client = f"Votre livraison a été reportée au {nouvelle_date}"

    livraison.save()

    # Email au client
    for commande in commandes:
        send_mail(
            subject="Mise à jour de votre livraison",
            message=message_client,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[commande.user.email],
            fail_silently=True
        )

        enregistrer_action(
            user,
            f"Action {action} sur livraison {livraison.id}"
        )

from django.db.models.functions import TruncDate
from django.db.models import Count

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils.timezone import now, timedelta
from store.models.delivery import Livraison
from store.models.order import Commande
from django.core.exceptions import PermissionDenied

def get_dashboard_graph_data(user):
    # Vérification rôle
    if user.role != "livreur":
        raise PermissionDenied("Accès réservé aux livreurs")

    # Livraisons du livreur
    livraisons = Livraison.objects.filter(livreur__utilisateur=user)

    # Comptage par statut pour graphique
    statuts = livraisons.values('etat').annotate(count=Count('id'))
    chart_status = {s['etat']: s['count'] for s in statuts}

    # Récupérer toutes les commandes livrées de ces livraisons
    commandes_livrees = Commande.objects.filter(
        livraison__in=livraisons,
        statut="LIVREE"
    ).count()

    # Comptages statistiques
    en_attente = livraisons.filter(etat="EN_ATTENTE").count()
    en_cours = livraisons.filter(etat="EN_COURS").count()
    livrees = livraisons.filter(etat="LIVREE").count()
    annulees = livraisons.filter(etat="ANNULEE").count()

    # Livraisons prévues aujourd'hui
    today = now().date()
    livraisons_aujourdhui = livraisons.filter(
        etat="EN_COURS",
        date_livraison__date=today
    ).count()

    # Livraisons par jour (dernière semaine) pour graphique
    last_week = today - timedelta(days=7)
    livraisons_semaine = (
        livraisons.filter(date_livraison__date__gte=last_week)
                  .annotate(day=TruncDate('date_livraison'))
                  .values('day')
                  .annotate(count=Count('id'))
                  .order_by('day')
    )
    chart_week = {str(item['day']): item['count'] for item in livraisons_semaine}

    return {
        "chart_status": chart_status,
        "chart_week": chart_week,
        "commandes_livrees": commandes_livrees,
        "en_attente": en_attente,
        "en_cours": en_cours,
        "livrees": livrees,
        "annulees": annulees,
        "livraisons_aujourdhui": livraisons_aujourdhui,
    }
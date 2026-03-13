from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.services_accounts import verifier_acces_admin
from django.contrib import messages

from accounts.services_accounts import (
    supprimer_utilisateur,
    creer_utilisateur
)
from accounts.models import Utilisateur

from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.utils.timezone import now
from calendar import monthrange

from store.models.product import Produit
from store.models.order import Commande
from accounts.models import Client

@login_required
def index(request):
    verifier_acces_admin(request.user)
    total_produits = Produit.objects.count()
    total_commandes = Commande.objects.count()
    total_clients = Utilisateur.objects.filter(role="client").count()

    dernieres_commandes = (
        Commande.objects
        .select_related("user", "paiement")
        .order_by("-date_commande")[:3]
    )

    today = now()
    last_day = monthrange(today.year, today.month)[1]

    jours_mois = list(range(1, last_day + 1))
    ventes_dict = {day: 0 for day in jours_mois}

    ventes = (
        Commande.objects
        .filter(
            date_commande__year=today.year,
            date_commande__month=today.month,
        )
        .annotate(jour=TruncDay("date_commande"))
        .values("jour")
        .annotate(total=Sum("paiement__montant_total"))
    )

    for vente in ventes:
        day = vente["jour"].day
        ventes_dict[day] = float(vente["total"] or 0)

    ventes_mois = list(ventes_dict.values())

    produits_par_categorie = (
        Produit.objects
        .values("sous_categorie__categorie__nom")
        .annotate(total=Count("id"))
    )

    categories = []
    quantites = []

    for item in produits_par_categorie:
        categories.append(item["sous_categorie__categorie__nom"] or "Sans catégorie")
        quantites.append(item["total"])

    context = {
        "total_produits": total_produits,
        "total_commandes": total_commandes,
        "total_clients": total_clients,
        "dernieres_commandes": dernieres_commandes,
        "ventes_mois": ventes_mois,
        "jours_mois": jours_mois,
        "categories": categories,
        "quantites": quantites,
    }

    return render(request, "dashboard/index.html", context)

# =========================
# LISTE DES UTILISATEURS
# =========================
@login_required
def utilisateurs_liste(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, "dashboard/utilisateurs/liste.html", {"utilisateurs": utilisateurs})


# =========================
# SUPPRIMER UTILISATEUR
# =========================
@login_required
def utilisateurs_supprimer(request, utilisateur_id):
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    supprimer_utilisateur(request.user, utilisateur)
    messages.success(request, f"Utilisateur {utilisateur.username} supprimé.")
    return redirect("dashboard:utilisateurs_liste")
# dashboard/views/utilisateurs.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from accounts.services_accounts import modifier_utilisateur  # logique métier

Utilisateur = get_user_model()

# =========================
# MODIFIER UN UTILISATEUR
# =========================
@login_required
def utilisateur_modifier(request, utilisateur_id):
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    if request.method == "POST":
        data = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "role": request.POST.get("role"),
            "is_active": request.POST.get("is_active") == "on",
        }

        # Si tu veux gérer le mot de passe
        password = request.POST.get("password")
        if password:
            data["password"] = password

        # Appel de la logique métier pour modifier l'utilisateur
        modifier_utilisateur(request.user, utilisateur, **data)

        messages.success(request, f"Utilisateur {utilisateur.username} modifié avec succès.")
        return redirect("dashboard:utilisateurs_liste")

    return render(request, "dashboard/utilisateurs/modifier.html", {"utilisateur": utilisateur})
# CREER UN UTILISATEUR
# =========================
@login_required
def utilisateur_creer(request):
    if request.method == "POST":
        data = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "role": request.POST.get("role"),
            "password": request.POST.get("password"),
        }

        # Appel de la logique métier pour créer l'utilisateur
        utilisateur = creer_utilisateur(request.user, **data)

        messages.success(request, f"Utilisateur {utilisateur.username} créé avec succès.")
        return redirect("dashboard:utilisateurs_liste")

    return render(request, "dashboard/utilisateurs/creer.html")
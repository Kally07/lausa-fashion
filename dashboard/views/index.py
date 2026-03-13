from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.utils.timezone import now
from calendar import monthrange

from store.models.product import Produit
from store.models.order import Commande
from accounts.models import Client


def dashboard_view(request):

    # 📊 Statistiques générales
    total_produits = Produit.objects.count()
    total_commandes = Commande.objects.count()
    total_clients = Client.objects.count()  # 🔹 CHANGEMENT

    # 🧾 3 Dernières commandes
    dernieres_commandes = (
        Commande.objects
        .select_related("user")
        .order_by("-date_commande")[:3]   # 🔹 CHANGEMENT
    )

    # ==========================
    # 📅 Ventes du mois
    # ==========================
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
        ventes_dict[day] = float(vente["total"])

    ventes_mois = list(ventes_dict.values())

    # ==========================
    # 📊 Produits par catégorie
    # ==========================
    produits_par_categorie = (
        Produit.objects
        .values("categorie__nom")
        .annotate(total=Count("id"))
    )

    categories = []
    quantites = []

    for item in produits_par_categorie:
        categories.append(item["categorie__nom"])
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

    return render(request, "dashboard/dashboard.html", context)
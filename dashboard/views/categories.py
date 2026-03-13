# dashboard/views/categories.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.services_accounts import verifier_acces_admin
from dashboard.services_dashboard import (
    creer_categorie,
    modifier_categorie,
    supprimer_categorie,
)
from store.models.product import Categorie


# =========================
# LISTE DES CATEGORIES
# =========================
@login_required
def liste_categories(request):
    verifier_acces_admin(request.user)

    categories = Categorie.objects.all()
    return render(
        request,
        "dashboard/categories/liste.html",
        {"categories": categories},
    )


# =========================
# CREER CATEGORIE
# =========================
@login_required
def categories_creer(request):
    verifier_acces_admin(request.user)

    if request.method == "POST":
        nom = request.POST.get("nom")
        description = request.POST.get("description")

        categorie = creer_categorie(
            request.user,
            nom=nom,
            description=description,
        )

        messages.success(request, f"Catégorie « {categorie.nom} » créée avec succès.")
        return redirect("dashboard:categories_liste")

    return render(request, "dashboard/categories/creer.html")


# =========================
# MODIFIER CATEGORIE
# =========================
@login_required
def categories_modifier(request, categorie_id):
    verifier_acces_admin(request.user)

    categorie = get_object_or_404(Categorie, id=categorie_id)

    if request.method == "POST":
        nom = request.POST.get("nom")
        description = request.POST.get("description")

        modifier_categorie(
            request.user,
            categorie,
            nom=nom,
            description=description,
        )

        messages.success(request, f"Catégorie « {categorie.nom} » modifiée avec succès.")
        return redirect("dashboard:categories_liste")

    return render(
        request,
        "dashboard/categories/modifier.html",
        {"categorie": categorie},
    )


# =========================
# SUPPRIMER CATEGORIE
# =========================
@login_required
def categories_supprimer(request, categorie_id):
    verifier_acces_admin(request.user)

    categorie = get_object_or_404(Categorie, id=categorie_id)
    supprimer_categorie(request.user, categorie)

    messages.success(request, f"Catégorie « {categorie.nom} » supprimée avec succès.")
    return redirect("dashboard:categories_liste")

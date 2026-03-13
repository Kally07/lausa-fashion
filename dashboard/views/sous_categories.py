# dashboard/views/sous_categories.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.services_accounts import verifier_acces_admin
from dashboard.services_dashboard import (
    creer_sous_categorie,
    modifier_sous_categorie,
    supprimer_sous_categorie,
)
from store.models.product import SousCategorie, Categorie


# =========================
# LISTE DES sous_categorieS
# =========================
@login_required
def liste_sous_categories(request):
    verifier_acces_admin(request.user)

    sous_categories = SousCategorie.objects.all()
    return render(
        request,
        "dashboard/sous_categories/liste.html",
        {"sous_categories": sous_categories},
    )


# =========================
# CREER sous_categorie
# =========================

@login_required
def sous_categories_creer(request):
    verifier_acces_admin(request.user)

    if request.method == "POST":
        nom = request.POST.get("nom")
        description = request.POST.get("description")
        categorie_id = request.POST.get("categorie_id")

        if not categorie_id:
            messages.error(request, "Veuillez choisir une catégorie.")
            return redirect("dashboard:sous_categories_creer")

        sous_categorie = creer_sous_categorie(
            user=request.user,
            categorie_id=categorie_id,
            nom=nom,
            description=description,
        )

        messages.success(
            request,
            f"Sous-catégorie « {sous_categorie.nom} » créée avec succès."
        )
        return redirect("dashboard:sous_categories_liste")

    categories = Categorie.objects.all()
    return render(
        request,
        "dashboard/sous_categories/creer.html",
        {"categories": categories}
    )


# =========================
# MODIFIER sous_categorie
# =========================
@login_required
def sous_categories_modifier(request, sous_categorie_id):
    verifier_acces_admin(request.user)

    sous_categorie = get_object_or_404(SousCategorie, id=sous_categorie_id)

    if request.method == "POST":
        nom = request.POST.get("nom")
        description = request.POST.get("description")

        modifier_sous_categorie(
            request.user,
            sous_categorie,
            nom=nom,
            description=description,
        )

        messages.success(request, f"Catégorie « {sous_categorie.nom} » modifiée avec succès.")
        return redirect("dashboard:sous_categories_liste")

    return render(
        request,
        "dashboard/sous_categories/modifier.html",
        {"sous_categorie": sous_categorie},
    )


# =========================
# SUPPRIMER sous_categorie
# =========================
@login_required
def sous_categories_supprimer(request, sous_categorie_id):
    verifier_acces_admin(request.user)

    sous_categorie = get_object_or_404(SousCategorie, id=sous_categorie_id)
    supprimer_sous_categorie(request.user, sous_categorie)

    messages.success(request, f"Catégorie « {sous_categorie.nom} » supprimée avec succès.")
    return redirect("dashboard:sous_categories_liste")

# dashboard/views/produits.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError



from dashboard.services_dashboard import (
    creer_ou_maj_produit,
    modifier_produit,
    supprimer_produit,
    lister_produits,
    lister_categories,
    lister_sous_categories,
    sous_categories_par_categorie
)
from store.models.product import Produit, Categorie, SousCategorie

# =========================
# LISTE DES PRODUITS
# =========================
@login_required
def liste_produits(request):
    # Récupération des filtres
    query = request.GET.get("q")
    categorie_id = request.GET.get("categorie")
    sous_categorie_id = request.GET.get("sous_categorie")

    # Liste des produits filtrés
    produits = lister_produits(
        user=request.user,
        query=query,
        categorie_id=categorie_id,
        sous_categorie_id=sous_categorie_id,
    )

    # Catégories pour le filtre
    categories = lister_categories(request.user)

    # Sous-catégories filtrées si une catégorie est sélectionnée
    if categorie_id:
        sous_categories = lister_sous_categories(request.user, categorie_id=categorie_id)
    else:
        sous_categories = lister_sous_categories(request.user)

    context = {
        "produits": produits,
        "categories": categories,
        "sous_categories": sous_categories,
        "q": query,
        "categorie_id": categorie_id,
        "sous_categorie_id": sous_categorie_id,
    }

    return render(request, "dashboard/produits/liste.html", context)

@login_required
def ajax_sous_categories(request, categorie_id):
    sous_categories = sous_categories_par_categorie(categorie_id)

    return JsonResponse(
        [{"id": sc.id, "nom": sc.nom} for sc in sous_categories],
        safe=False
    )

# =========================
# CREER PRODUIT
# =========================
@login_required
def produits_creer(request):
    sous_categories = SousCategorie.objects.all()
    produits = Produit.objects.all()  # Pour remplir le select des produits existants

    if request.method == "POST":
        produit_existant_id = request.POST.get("produit_existant_id")
        nom = request.POST.get("nom")
        prix = request.POST.get("prix")
        stock = request.POST.get("stock")
        description = request.POST.get("description")
        sous_categorie_id = request.POST.get("sous_categorie_id")
        image = request.FILES.get("image")

        sous_categorie = None
        if sous_categorie_id:
            sous_categorie = get_object_or_404(SousCategorie, id=sous_categorie_id)

        # Si produit existant choisi, on met à jour son stock
        if produit_existant_id:
            produit = get_object_or_404(Produit, id=produit_existant_id)
            try:
                stock = int(stock)
                if stock < 0:
                    raise ValueError("La quantité doit être positive.")
                produit.stock += stock
                produit.save()
                messages.success(request, f"Stock mis à jour pour {produit.nom}")
                return redirect("dashboard:produits_liste")
            except ValueError as e:
                messages.error(request, str(e))
        else:
            # Sinon création d'un nouveau produit via le service
            try:
                produit = creer_ou_maj_produit(
                    user=request.user,
                    nom=nom,
                    prix=prix,
                    stock=stock,
                    description=description,
                    sous_categorie=sous_categorie,
                    image=image
                )
                messages.success(request, f"Produit {produit.nom} créé avec succès.")
                return redirect("dashboard:produits_liste")
            except ValidationError as e:
                messages.error(request, str(e))

    return render(request, "dashboard/produits/creer.html", {
        "sous_categories": sous_categories,
        "produits": produits
    })



# =========================
# MODIFIER PRODUIT
# =========================
@login_required
def produits_modifier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    sous_categories = SousCategorie.objects.all()

    if request.method == "POST":
        data = {
            "nom": request.POST.get("nom"),
            "prix": request.POST.get("prix"),
            "description": request.POST.get("description"),
            "stock": request.POST.get("stock"),
            "sous_categorie_id": request.POST.get("sous_categorie_id"),
        }
        if request.FILES.get("image"):
            data["image"] = request.FILES.get("image")

        modifier_produit(request.user, produit, **data)
        messages.success(request, f"Produit {produit.nom} modifié avec succès.")
        return redirect("dashboard:produits_liste")

    return render(request, "dashboard/produits/modifier.html", {
        "produit": produit,
        "sous_categories": sous_categories
    })

# =========================
# SUPPRIMER PRODUIT
# =========================
@login_required
def produits_supprimer(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    supprimer_produit(request.user, produit)
    messages.success(request, f"Produit {produit.nom} supprimé avec succès.")
    return redirect("dashboard:produits_liste")

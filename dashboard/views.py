# dashboard/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages

from store.models.product import Produit
from store.models.order import Commande
from store.models.delivery import Livraison
from accounts.models import Utilisateur, Livreur

from dashboard.services_dashboard import (
    verifier_admin,

    # produits
    creer_produit,
    modifier_produit,
    supprimer_produit,

    # commandes
    creer_commande,
    modifier_commande,
    supprimer_commande,
    valider_commande,
    annuler_commande,
    rechercher_commandes,

    # livraisons
    creer_livraison,
    terminer_livraison,

    # utilisateurs
    activer_utilisateur,
    desactiver_utilisateur,
    supprimer_utilisateur,

    # livreurs
    changer_statut_livreur,
)


# =========================
# DASHBOARD HOME
# =========================

@login_required
def index(request):
    verifier_admin(request.user)

    context = {
        "total_produits": Produit.objects.count(),
        "total_commandes": Commande.objects.count(),
        "total_livraisons": Livraison.objects.count(),
        "recent_commandes": Commande.objects.order_by("-date_commande")[:5],
    }

    return render(request, "dashboard/index.html", context)


# =========================
# PRODUITS
# =========================

@login_required
def liste_produits(request):
    verifier_admin(request.user)
    produits = Produit.objects.all()
    return render(request, "dashboard/produits/liste.html", {"produits": produits})


@login_required
def ajouter_produit(request):
    verifier_admin(request.user)

    if request.method == "POST":
        creer_produit(
            request.user,
            nom=request.POST.get("nom"),
            prix=request.POST.get("prix"),
            stock=request.POST.get("stock"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
            categorie_id=request.POST.get("categorie"),
        )
        messages.success(request, "Produit créé avec succès")
        return redirect("dashboard:produits")

    return render(request, "dashboard/produits/ajouter.html")


@login_required
def modifier_produit_view(request, produit_id):
    verifier_admin(request.user)
    produit = get_object_or_404(Produit, id=produit_id)

    if request.method == "POST":
        modifier_produit(
            request.user,
            produit,
            nom=request.POST.get("nom"),
            prix=request.POST.get("prix"),
            stock=request.POST.get("stock"),
            description=request.POST.get("description"),
            image=request.FILES.get("image") or produit.image,
        )
        messages.success(request, "Produit modifié")
        return redirect("dashboard:produits")

    return render(request, "dashboard/produits/modifier.html", {"produit": produit})


@login_required
def supprimer_produit_view(request, produit_id):
    verifier_admin(request.user)
    produit = get_object_or_404(Produit, id=produit_id)
    supprimer_produit(request.user, produit)
    messages.success(request, "Produit supprimé")
    return redirect("dashboard:produits")


# =========================
# COMMANDES
# =========================

@login_required
def liste_commandes(request):
    verifier_admin(request.user)

    query = request.GET.get("q")
    if query:
        commandes = rechercher_commandes(request.user, query)
    else:
        commandes = Commande.objects.all().order_by("-date_commande")

    return render(request, "dashboard/commandes/liste.html", {"commandes": commandes})


@login_required
def detail_commande(request, commande_id):
    verifier_admin(request.user)
    commande = get_object_or_404(Commande, id=commande_id)
    return render(request, "dashboard/commandes/detail.html", {"commande": commande})


@login_required
def valider_commande_view(request, commande_id):
    verifier_admin(request.user)
    commande = get_object_or_404(Commande, id=commande_id)
    valider_commande(request.user, commande)
    messages.success(request, "Commande validée")
    return redirect("dashboard:commandes")


@login_required
def annuler_commande_view(request, commande_id):
    verifier_admin(request.user)
    commande = get_object_or_404(Commande, id=commande_id)

    if request.method == "POST":
        motif = request.POST.get("motif", "")
        annuler_commande(request.user, commande, motif)
        messages.warning(request, "Commande annulée")
        return redirect("dashboard:commandes")

    return render(request, "dashboard/commandes/annuler.html", {"commande": commande})


@login_required
def supprimer_commande_view(request, commande_id):
    verifier_admin(request.user)
    commande = get_object_or_404(Commande, id=commande_id)
    supprimer_commande(request.user, commande)
    messages.success(request, "Commande supprimée")
    return redirect("dashboard:commandes")


# =========================
# LIVRAISONS
# =========================

@login_required
def liste_livraisons(request):
    verifier_admin(request.user)
    livraisons = Livraison.objects.all().order_by("-date_livraison")
    return render(request, "dashboard/livraisons/liste.html", {"livraisons": livraisons})


@login_required
def creer_livraison_view(request):
    verifier_admin(request.user)

    if request.method == "POST":
        livreur = get_object_or_404(Livreur, id=request.POST.get("livreur"))
        commandes_ids = request.POST.getlist("commandes")
        commandes = Commande.objects.filter(id__in=commandes_ids)

        creer_livraison(request.user, livreur, commandes)
        messages.success(request, "Livraison créée")
        return redirect("dashboard:livraisons")

    context = {
        "livreurs": Livreur.objects.filter(statut=True),
        "commandes": Commande.objects.filter(statut="VALIDE"),
    }
    return render(request, "dashboard/livraisons/ajouter.html", context)


@login_required
def terminer_livraison_view(request, livraison_id):
    verifier_admin(request.user)
    livraison = get_object_or_404(Livraison, id=livraison_id)
    terminer_livraison(request.user, livraison)
    messages.success(request, "Livraison terminée")
    return redirect("dashboard:livraisons")


# =========================
# UTILISATEURS
# =========================

from django.db.models import Q
from dashboard.models import Utilisateur

@login_required
def liste_utilisateurs(request):
    query = request.GET.get("q", "")        # Recherche par nom ou email
    role_filter = request.GET.get("role", "")  # Filtre par rôle

    utilisateurs = Utilisateur.objects.all()

    if query:
        utilisateurs = utilisateurs.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    if role_filter:
        utilisateurs = utilisateurs.filter(role=role_filter)

    utilisateurs = utilisateurs.order_by("username")

    return render(request, "dashboard/utilisateurs/liste.html", {
        "utilisateurs": utilisateurs,
        "query": query,
        "role_filter": role_filter,
    })


@login_required
def activer_utilisateur_view(request, user_id):
    verifier_admin(request.user)
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    activer_utilisateur(request.user, utilisateur)
    return redirect("dashboard:utilisateurs")


@login_required
def desactiver_utilisateur_view(request, user_id):
    verifier_admin(request.user)
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    desactiver_utilisateur(request.user, utilisateur)
    return redirect("dashboard:utilisateurs")


@login_required
def supprimer_utilisateur_view(request, user_id):
    verifier_admin(request.user)
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    supprimer_utilisateur(request.user, utilisateur)
    return redirect("dashboard:utilisateurs")


# =========================
# LIVREURS
# =========================

@login_required
def changer_statut_livreur_view(request, livreur_id):
    verifier_admin(request.user)
    livreur = get_object_or_404(Livreur, id=livreur_id)
    changer_statut_livreur(request.user, livreur, not livreur.statut)
    return redirect("dashboard:livreurs")

# =========================
# PAIEMENTS
# =========================

from store.models.payment import PaiementCommande

@login_required
def liste_paiements(request):
    verifier_admin(request.user)
    paiements = PaiementCommande.objects.select_related("commande").order_by("-date_paiement")
    return render(request, "dashboard/paiements/liste.html", {"paiements": paiements})

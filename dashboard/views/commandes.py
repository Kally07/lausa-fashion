# dashboard/views/commandes.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from dashboard.services_dashboard import (
    liste_commandes,
    liste_commandes_par_statut,
    creer_commande,
    modifier_commande,
    supprimer_commande,
    valider_commande,
    annuler_commande,
    rechercher_commandes
)
from store.models.order import Commande
from accounts.models import Utilisateur

# =========================
# LISTE DES COMMANDES
# =========================
@login_required
def commandes_liste(request):
    commandes = liste_commandes(request.user)
    return render(request, "dashboard/commandes/liste.html", {"commandes": commandes})

# =========================
# CREER COMMANDE
# =========================
@login_required
def commandes_creer(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user_client = get_object_or_404(Utilisateur, id=user_id)
        lignes = []  # tu peux récupérer depuis un formulaire ou panier
        adresse = request.POST.get("adresse")
        telephone = request.POST.get("telephone")
        commande = creer_commande(request.user, user_client, lignes, adresse, telephone)
        messages.success(request, f"Commande {commande.id} créée avec succès.")
        return redirect("dashboard:commandes_liste")
    utilisateurs = Utilisateur.objects.filter(role="client")
    return render(request, "dashboard/commandes/creer.html", {"utilisateurs": utilisateurs})

# =========================
# MODIFIER COMMANDE
# =========================
@login_required
def commandes_modifier(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    if request.method == "POST":
        data = {
            "adresse": request.POST.get("adresse"),
            "telephone": request.POST.get("telephone")
        }
        modifier_commande(request.user, commande, **data)
        messages.success(request, f"Commande {commande.id} modifiée avec succès.")
        return redirect("dashboard:commandes_liste")
    return render(request, "dashboard/commandes/modifier.html", {"commande": commande})

# =========================
# SUPPRIMER COMMANDE
# =========================
@login_required
def commandes_supprimer(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    supprimer_commande(request.user, commande)
    messages.success(request, f"Commande {commande.id} supprimée avec succès.")
    return redirect("dashboard:commandes_liste")

# =========================
# VALIDER COMMANDE
# =========================
@login_required
def commandes_valider(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    valider_commande(request.user, commande)
    messages.success(request, f"Commande {commande.id} validée.")
    return redirect("dashboard:commandes_liste")

# =========================
# ANNULER COMMANDE
# =========================
@login_required
def commandes_annuler(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    motif = request.POST.get("motif", "")
    annuler_commande(request.user, commande, motif)
    messages.success(request, f"Commande {commande.id} annulée.")
    return redirect("dashboard:commandes_liste")

# =========================
# RECHERCHER COMMANDES
# =========================
@login_required
def commandes_rechercher(request):
    query = request.GET.get("q", "")
    commandes = rechercher_commandes(request.user, query)
    return render(request, "dashboard/commandes/liste.html", {"commandes": commandes, "query": query})

@login_required
def commandes_en_attente(request):
    commandes = liste_commandes_par_statut(request.user, "EN_ATTENTE")
    return render(
        request,
        "dashboard/commandes/liste.html",
        {
            "commandes": commandes,
            "filtre": "EN_ATTENTE"
        }
    )

@login_required
def commandes_validees(request):
    commandes = liste_commandes_par_statut(request.user, "VALIDE")
    return render(
        request,
        "dashboard/commandes/liste.html",
        {
            "commandes": commandes,
            "filtre": "VALIDE"
        }
    )

@login_required
def commandes_annulees(request):
    commandes = liste_commandes_par_statut(request.user, "ANNULEE")
    return render(
        request,
        "dashboard/commandes/liste.html",
        {
            "commandes": commandes,
            "filtre": "ANNULEE"
        }
    )

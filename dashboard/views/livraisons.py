# dashboard/views/livraisons.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from dashboard.services_dashboard import (
    creer_livraison,
    terminer_livraison
)
from store.models.delivery import Livraison
from accounts.models import Livreur
from store.models.order import Commande

# =========================
# LISTE DES LIVRAISONS
# =========================
@login_required
def livraisons_liste(request):
    livraisons = Livraison.objects.all().order_by("-date_livraison")
    return render(request, "dashboard/livraisons/liste.html", {"livraisons": livraisons})

# =========================
# CREER LIVRAISON
# =========================
@login_required
def livraisons_creer(request):
    if request.method == "POST":
        livreur_id = request.POST.get("livreur_id")
        commandes_ids = request.POST.getlist("commandes")
        livreur = get_object_or_404(Livreur, id=livreur_id)
        commandes = Commande.objects.filter(id__in=commandes_ids)
        livraison = creer_livraison(request.user, livreur, commandes)
        messages.success(request, f"Livraison {livraison.id} créée avec succès.")
        return redirect("dashboard:livraisons_liste")
    livreurs = Livreur.objects.filter(utilisateur__statut="actif")
    commandes = Commande.objects.filter(statut="EN_PREPARATION")
    return render(request, "dashboard/livraisons/creer.html", {"livreurs": livreurs, "commandes": commandes})

# =========================
# TERMINER LIVRAISON
# =========================
@login_required
def livraisons_terminer(request, livraison_id):
    livraison = get_object_or_404(Livraison, id=livraison_id)
    terminer_livraison(request.user, livraison)
    messages.success(request, f"Livraison {livraison.id} terminée.")
    return redirect("dashboard:livraisons_liste")

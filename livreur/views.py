from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
# Create your views here.


@login_required
def dashboard_livreur(request):    
    data_stats = services_livreur.get_dashboard_data(request.user)
    data_charts = services_livreur.get_dashboard_graph_data(request.user)
    context = {**data_stats, **data_charts}
    if request.user.role != "livreur":
        raise PermissionDenied
    return render(request, "livreur/index.html", context)

# livreur/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from . import services_livreur


# =====================================================
# Dashboard
# =====================================================

@login_required
def dashboard(request):
    data = services_livreur.get_dashboard_data(request.user)

    return render(request, "livreur/dashboard.html", data)


# =====================================================
# Liste livraisons
# =====================================================

@login_required
def livraisons_liste(request):
    livraisons = services_livreur.get_livraisons_livreur(request.user)

    return render(request, "livreur/livraisons_liste.html", {
        "livraisons": livraisons
    })


# =====================================================
# Détail livraison
# =====================================================

@login_required
def livraison_detail(request, livraison_id):
    livraison, commandes = services_livreur.get_livraison_detail(
        request.user,
        livraison_id
    )

    return render(request, "livreur/livraison_detail.html", {
        "livraison": livraison,
        "commandes": commandes
    })


# =====================================================
# Modifier statut
# =====================================================

@login_required
def modifier_statut(request, livraison_id):
    if request.method == "POST":
        nouveau_statut = request.POST.get("etat")

        services_livreur.mettre_a_jour_statut_livraison(
            request.user,
            livraison_id,
            nouveau_statut
        )

        messages.success(request, "Statut mis à jour avec succès.")

    return redirect("livreur:livraison_detail", livraison_id=livraison_id)

@login_required
def livraison_detail(request, livraison_id):

    if request.method == "POST":
        action = request.POST.get("action")
        motif = request.POST.get("motif")
        nouvelle_date = request.POST.get("nouvelle_date")

        services_livreur.traiter_action_livraison(
            request.user,
            livraison_id,
            action,
            motif,
            nouvelle_date
        )

        messages.success(request, "Action effectuée avec succès.")
        return redirect("livreur:livraison_detail", livraison_id=livraison_id)

    livraison, commandes = services_livreur.get_livraison_detail(
        request.user,
        livraison_id
    )

    return render(request, "livreur/livraison_detail.html", {
        "livraison": livraison,
        "commandes": commandes
    })
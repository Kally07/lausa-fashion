from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from accounts.models import Utilisateur, Livreur
from accounts.services_accounts import (
    creer_livreur,
    lister_livreurs,
    modifier_livreur,
    supprimer_livreur
)

# =========================
# LISTE DES LIVREURS
# =========================
@login_required
def livreurs_liste(request):
    # Récupère tous les profils livreurs
    livreurs = lister_livreurs(request.user)
    return render(request, "dashboard/livreurs/liste.html", {"livreurs": livreurs})


# =========================
# CREER UN NOUVEAU LIVREUR (utilisateur + profil)
# =========================
@login_required
def livreur_creer(request):
    if request.method == "POST":
        try:
            livreur = creer_livreur(
                admin=request.user,
                username=request.POST.get("username"),
                password=request.POST.get("password"),
                email=request.POST.get("email", ""),
                telephone=request.POST.get("telephone", ""),
                moyen_transport=request.POST.get("moyen_transport", "")
            )

            messages.success(
                request,
                f"Livreur {livreur.utilisateur.username} créé avec succès."
            )
            return redirect("dashboard:livreurs_liste")

        except ValidationError as e:
            messages.error(request, e.message)

    return render(request, "dashboard/livreurs/creer.html")

# =========================
# ASSOCIER UN UTILISATEUR EXISTANT
# =========================
@login_required
def livreur_associer(request):
    if request.method == "POST":
        utilisateur_id = request.POST.get("utilisateur_id")
        moyen_transport = request.POST.get("moyen_transport", "")
        telephone = request.POST.get("telephone", "")

        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

        # Vérifie qu'il n'est pas déjà un livreur
        if hasattr(utilisateur, "profil_livreur"):
            messages.error(request, f"L'utilisateur {utilisateur.username} est déjà un livreur.")
            return redirect("dashboard:livreurs_liste")

        # Création du profil livreur
        livreur = Livreur.objects.create(
            utilisateur=utilisateur,
            moyen_transport=moyen_transport,
            telephone=telephone,
            statut=True
        )
        messages.success(request, f"Utilisateur {utilisateur.username} associé comme livreur.")
        return redirect("dashboard:livreurs_liste")

    # Liste des utilisateurs existants qui ne sont pas encore des livreurs
    utilisateurs = Utilisateur.objects.filter(role="client").exclude(profil_livreur__isnull=False)
    return render(request, "dashboard/livreurs/associer.html", {"utilisateurs": utilisateurs})


# =========================
# MODIFIER LIVREUR
# =========================
@login_required
def livreurs_modifier(request, livreur_id):
    livreur = get_object_or_404(Livreur, id=livreur_id)

    if request.method == "POST":
        data = {
            "telephone": request.POST.get("telephone"),
            "moyen_transport": request.POST.get("moyen_transport"),
        }
        modifier_livreur(request.user, livreur, **data)
        messages.success(request, f"Livreur {livreur.utilisateur.username} modifié.")
        return redirect("dashboard:livreurs_liste")

    return render(request, "dashboard/livreurs/modifier.html", {"livreur": livreur})


# =========================
# SUPPRIMER LIVREUR
# =========================
@login_required
def livreurs_supprimer(request, livreur_id):
    livreur = get_object_or_404(Livreur, id=livreur_id)
    supprimer_livreur(request.user, livreur)
    messages.success(request, f"Livreur {livreur.utilisateur.username} supprimé.")
    return redirect("dashboard:livreurs_liste")

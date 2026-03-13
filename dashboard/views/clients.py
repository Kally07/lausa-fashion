# dashboard/views/clients.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from accounts.services_accounts import (
    lister_clients,
    creer_client,
    supprimer_client,
    modifier_utilisateur,
)
from accounts.models import Client


# =========================
# LISTE CLIENTS
# =========================
@login_required
def clients_liste(request):
    query = request.GET.get("q")
    clients = lister_clients(request.user)

    if query:
        clients = clients.filter(
            Q(utilisateur__username__icontains=query) |
            Q(nom__icontains=query) |
            Q(prenom__icontains=query)
        )

    return render(
        request,
        "dashboard/clients/liste.html",
        {
            "clients": clients,
            "query": query
        }
    )


# =========================
# CREER CLIENT
# =========================
@login_required
def client_creer(request):
    if request.method == "POST":
        client = creer_client(
            admin=request.user,   # ✅ OBLIGATOIRE
            username=request.POST.get("username"),
            password=request.POST.get("password"),
            email=request.POST.get("email"),
            nom=request.POST.get("nom"),
            prenom=request.POST.get("prenom"),
            telephone=request.POST.get("telephone"),
            adresse=request.POST.get("adresse"),
        )

        messages.success(
            request,
            f"Client {client.utilisateur.username} créé avec succès."
        )
        return redirect("dashboard:clients_liste")

    return render(request, "dashboard/clients/creer.html")


# =========================
# MODIFIER CLIENT
# =========================
@login_required
def client_modifier(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    utilisateur = client.utilisateur

    if request.method == "POST":
        data = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
        }

        password = request.POST.get("password")
        if password:
            data["password"] = password

        # Modifier utilisateur
        modifier_utilisateur(request.user, utilisateur, **data)

        # Modifier profil client
        client.nom = request.POST.get("nom")
        client.prenom = request.POST.get("prenom")
        client.telephone = request.POST.get("telephone")
        client.adresse = request.POST.get("adresse")
        client.save()

        messages.success(
            request,
            f"Client {utilisateur.username} modifié avec succès."
        )
        return redirect("dashboard:clients_liste")

    return render(
        request,
        "dashboard/clients/modifier.html",
        {"client": client}
    )


# =========================
# SUPPRIMER CLIENT
# =========================
@login_required
def clients_supprimer(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    supprimer_client(request.user, client)

    messages.success(
        request,
        f"Client {client.utilisateur.username} supprimé."
    )
    return redirect("dashboard:clients_liste")

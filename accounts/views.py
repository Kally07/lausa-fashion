from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import InscriptionForm, ConnexionForm, DevenirClientForm
from .services_accounts import rediriger_apres_connexion, devenir_client
from store.domain.services_mail import MailService

def inscription(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # connexion automatique
            MailService.send_registration_confirmation(user)
            return redirect("store:index")  # nouveau compte → store
    else:
        form = InscriptionForm()
    return render(request, "accounts/inscription.html", {"form": form})

def connexion(request):
    if request.method == "POST":
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return rediriger_apres_connexion(user)  # redirection selon rôle
    else:
        form = ConnexionForm()
    return render(request, "accounts/connexion.html", {"form": form})

@login_required
def deconnexion(request):
    logout(request)
    return redirect("store:index")

@login_required
def devenir_client_view(request):
    """
    Permet à un utilisateur connecté de devenir client
    """

    # Sécurité : si déjà client → redirection
    if hasattr(request.user, "profil_client"):
        messages.info(request, "Vous êtes déjà client.")
        return redirect("store:index")

    if request.method == "POST":
        form = DevenirClientForm(request.POST)

        if form.is_valid():
            try:
                devenir_client(
                    utilisateur=request.user,
                    nom=form.cleaned_data["nom"],
                    prenom=form.cleaned_data["prenom"],
                    telephone=form.cleaned_data.get("telephone", ""),
                    adresse=form.cleaned_data.get("adresse", "")
                )

                messages.success(
                    request,
                    "Votre profil client a été créé avec succès."
                )
                return redirect("store:index")

            except ValidationError as e:
                messages.error(request, e.message)

    else:
        form = DevenirClientForm()

    return render(
        request,
        "accounts/devenir_client.html",
        {"form": form}
    )
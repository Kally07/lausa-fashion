# dashboard/views/paiement.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from dashboard.services_dashboard import lister_paiements

@login_required
def liste_paiements(request):
    try:
        # Appel à la fonction du service
        paiements = lister_paiements(request.user)
    except PermissionDenied:
        return render(request, "dashboard/erreur_acces.html", {"message": "Accès refusé"})

    context = {
        "paiements": paiements
    }
    return render(request, "dashboard/paiements/liste.html", context)

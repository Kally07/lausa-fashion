from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from accounts.services_accounts import verifier_acces_admin
from store.models.history import Historique

@login_required
def historiques_liste(request):
    verifier_acces_admin(request.user)  # accès réservé aux admins
    historiques = Historique.objects.all().order_by("-date_action")

    query = request.GET.get("q")
    if query:
        historiques = historiques.filter(utilisateur__username__icontains=query)

    return render(request, "dashboard/historiques/liste.html", {
        "historiques": historiques,
        "query": query
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings

from store.models import Produit, Commande, Categorie, SousCategorie
from store.models.cart import Panier
from store.forms import RegisterForm
from store.domain.paiement_moncash import creer_paiement_moncash, valider_paiement_moncash

from store.domain.services import (
    # Panier
    ajouter_produit_au_panier,
    modifier_quantite_panier,
    supprimer_item_panier,
    vider_panier,
    obtenir_panier,
    obtenir_panier_actif,
    get_panier_count,

    # Commande / Paiement
    payer_panier,

    # Recherche
    rechercher_produits,
)

from store.domain.exceptions import (
    PanierVideError,
    PaiementInvalideError,
    StockInsuffisantError
)

# =====================================================
# AUTH
# =====================================================

class CustomLoginView(LoginView):
    template_name = "accounts/connexion.html"


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès.")
            return redirect("index")
        messages.error(request, "Formulaire invalide.")
    else:
        form = RegisterForm()

    return render(request, "store/register.html", {"form": form})

# =====================================================
# PAGES STATIQUES
# =====================================================

def index(request):
    context = {
        "derniers_produits": Produit.objects.order_by("-id")[:8],
        "categories": Categorie.objects.all()
    }
    return render(request, "store/index.html", context)


def apropos(request):
    return render(request, "store/a_propos.html")


def faq(request):
    return render(request, "store/faq.html")


def contact(request):
    success = False

    if request.method == "POST":
        send_mail(
            subject=f"Nouveau message de {request.POST.get('nom')}",
            message=(
                f"Email : {request.POST.get('email')}\n\n"
                f"Message :\n{request.POST.get('message')}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
        success = True

    return render(request, "store/contact.html", {"success": success})


@login_required
def profil_view(request):
    return render(request, "store/profil.html")

# =====================================================
# PRODUITS
# =====================================================

def liste_produits(request):
    return render(
        request,
        "store/produits.html",
        {"produits": Produit.objects.all()}
    )

# ===========================================
# DÉTAIL PRODUIT via POST
# ===========================================
@require_POST
def detail_produit(request):
    produit_id = request.POST.get("produit_id")
    produit = get_object_or_404(Produit, id=produit_id)

    return render(
        request,
        "store/detail_produit.html",
        {"produit": produit}
    )

# ===========================================
# PRODUITS PAR CATÉGORIE via POST
# ===========================================
@require_POST
def produits_par_categorie(request):
    categorie_id = request.POST.get("categorie_id")
    categorie = get_object_or_404(Categorie, id=categorie_id)
    produits = Produit.objects.filter(categorie=categorie)

    return render(
        request,
        "store/produits_par_categorie.html",
        {
            "categorie": categorie,
            "produits": produits
        }
    )

def produits_sous_categorie(request, sous_categorie_id):
    sous_categorie = get_object_or_404(SousCategorie, id=sous_categorie_id)
    produits = sous_categorie.produits.all()  # relation "related_name"
    
    return render(
        request,
        "store/produits_par_sous_categorie.html",
        {
            "sous_categorie": sous_categorie,
            "produits": produits
        }
    )

# =====================================================
# PANIER
# =====================================================

@login_required
def panier(request):
    try:
        items, total = obtenir_panier(request.user)
    except PanierVideError:
        items, total = [], 0

    return render(
        request,
        "store/panier.html",
        {
            "produits_panier": items,
            "total_panier": total
        }
    )

@login_required
@require_POST
def ajouter_au_panier(request):
    produit_id = request.POST.get("produit_id")
    produit = get_object_or_404(Produit, id=produit_id)
    quantite = int(request.POST.get("quantite", 1))

    try:
        item = ajouter_produit_au_panier(
            user=request.user,
            produit=produit,
            quantite=quantite
        )
        return JsonResponse({
            "success": True,
            "quantite": item.quantite,
            "message": f"{item.produit.nom} ajouté au panier."
        })
    except ValueError as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

@login_required
@require_POST
def mise_a_jour_panier_ajax(request):
    item_id = request.POST.get("item_id")
    action = request.POST.get("action")

    item = modifier_quantite_panier(
        request.user,
        item_id,
        action
    )

    if item is None:
        return JsonResponse({"deleted": True})

    return JsonResponse({
        "quantite": item.quantite,
        "total_item": item.total
    })


@login_required
@require_POST
def supprimer_du_panier(request):
    item_id = request.POST.get("item_id")
    if not item_id:
        return JsonResponse({"success": False, "error": "Item non spécifié."})
    
    supprimer_item_panier(request.user, item_id)

    # Retourne succès + nouveau compteur panier
    return JsonResponse({
        "success": True,
        "count": get_panier_count(request.user)
    })


@login_required
@require_POST
def vider_panier_view(request):
    vider_panier(request.user)
    messages.info(request, "Panier vidé.")
    return redirect("store:panier")


@login_required
@require_POST
def panier_count_ajax(request):
    return JsonResponse({
        "count": get_panier_count(request.user)
    })


@login_required
def paiement_moncash_view(request):
    """
    Vue pour générer le paiement MonCash et retourner l'URL pour l'iframe.
    """
    order_id = request.GET.get("order_id")
    panier = get_object_or_404(Panier, pk=order_id, actif=True)

    try:
        # Créer le paiement MonCash et récupérer l'URL de redirection
        redirect_url = creer_paiement_moncash(panier.total, panier.id)
    except PaiementInvalideError as e:
        messages.error(request, f"Erreur MonCash : {e}")
        return redirect("store:panier")

    # Affiche l'iframe MonCash via un template minimal
    return render(
        request,
        "store/paiement_moncash_iframe.html",
        {"redirect_url": redirect_url, "panier": panier}
    )

@login_required
def paiement_moncash_success(request):
    transaction_id = request.GET.get("transactionId")
    order_id = request.GET.get("orderId")

    panier = get_object_or_404(Panier, pk=order_id, actif=True)

    try:
        # Validation automatique
        valider_paiement_moncash(transaction_id, panier.total, use_transaction_id=True)

        commande, paiement = payer_panier(
            user=request.user,
            mode_paiement="MonCash",
            reference=transaction_id,
            adresse="Adresse confirmée",
            telephone="Confirmé",
            date_livraison=None
        )

        messages.success(request, "Paiement réussi 🎉")
        return redirect("store:mes_commandes")

    except PaiementInvalideError:
        messages.error(request, "Paiement non validé.")
        return redirect("store:panier")

@login_required
def paiement_moncash_cancel(request):
    messages.warning(request, "Paiement annulé.")
    return redirect("store:panier")

# =====================================================
# COMMANDE
# =====================================================

@login_required
@require_POST
def valider_commande(request):
    try:
        adresse = request.POST.get("adresse")
        telephone = request.POST.get("telephone")
        date_livraison = request.POST.get("date_livraison")
        mode_paiement = request.POST.get("mode_paiement")
        reference = request.POST.get("reference")
        if date_livraison:
            date_livraison_obj = date.fromisoformat(date_livraison)

            if date_livraison_obj < date.today():
                return JsonResponse({
                    "success": False,
                    "message": "La date de livraison ne peut pas être antérieure à aujourd'hui."
                })
            
        commande, _ = payer_panier(
            user=request.user,
            mode_paiement=mode_paiement,
            reference=reference,
            adresse=adresse,
            telephone=telephone,
            date_livraison=date_livraison
        )
        messages.success(
            request,
            f"Commande #{commande.id} validée avec succès."
        )
        return redirect("store:mes_commandes")

    except (PanierVideError, PaiementInvalideError, StockInsuffisantError) as e:
        messages.error(request, str(e))
        return redirect("store:panier")


@login_required
def valider_commande_view(request):
    """
    Affiche le formulaire de validation de commande avec les options
    MonCash, NatCash, CarteDeCredit.
    """
    try:
        items, total = obtenir_panier(request.user)
        panier = obtenir_panier_actif(request.user)
    except PanierVideError:
        items, total = [], 0
        panier = None

    if request.method == "POST":
        adresse = request.POST.get("adresse")
        telephone = request.POST.get("telephone")
        date_livraison = request.POST.get("date_livraison")
        mode_paiement = request.POST.get("mode_paiement")
        reference = request.POST.get("reference")
        if date_livraison:
            date_livraison_obj = date.fromisoformat(date_livraison)

            if date_livraison_obj < date.today():
                return JsonResponse({
                    "success": False,
                    "message": "La date de livraison ne peut pas être antérieure à aujourd'hui."
                })
        try:
            # Appel au service de paiement
            commande, paiement = payer_panier(
                user=request.user,
                mode_paiement=mode_paiement,
                reference=reference,
                adresse=adresse,
                telephone=telephone,
                date_livraison=date_livraison
            )
            messages.success(
                request,
                f"Commande #{commande.id} validée avec succès."
            )
            return redirect("store:mes_commandes")

        except (PanierVideError, PaiementInvalideError, StockInsuffisantError) as e:
            messages.error(request, str(e))
            return redirect("store:panier")

    # GET → afficher le formulaire
    return render(
        request,
        "store/valider_comande.html",
        {
            "panier": panier,
            "produits_panier": items,
            "total_panier": total,
        }
    )

@login_required
def mes_commandes(request):
    commandes = (
        Commande.objects
        .filter(user=request.user)
        .order_by("-date_commande")
    )

    return render(
        request,
        "store/mes_commandes.html",
        {"commandes": commandes}
    )


@login_required
def detail_commande(request, commande_id):
    commande = get_object_or_404(
        Commande,
        id=commande_id,
        user=request.user
    )

    return render(
        request,
        "store/detail_commande.html",
        {"commande": commande}
    )

# =====================================================
# RECHERCHE
# =====================================================

def recherche(request):
    produits = []
    mot_clef = ""

    if request.method == "POST":
        mot_clef = request.POST.get("q", "").strip()
        produits = rechercher_produits(request.user, mot_clef)

    return render(
        request,
        "store/recherche.html",
        {
            "produits": produits,
            "mot_clef": mot_clef
        }
    )


""""
@login_required
def paiement_natcash_view(request):
    
    #Vue pour l'iframe NatCash.
    
    order_id = request.GET.get("order_id")
    panier = get_object_or_404(Panier, pk=order_id, actif=True)

    # Créer le paiement NatCash et récupérer l'URL de redirection
    redirect_url = creer_paiement_natcash(panier.total, panier.id)

    return redirect(redirect_url)


@login_required
def paiement_carte_view(request):
    
    #Vue pour l'iframe CarteDeCredit.
    
    order_id = request.GET.get("order_id")
    panier = get_object_or_404(Panier, pk=order_id, actif=True)

    # Créer le paiement via le service CarteDeCredit
    redirect_url = creer_paiement_carte(panier.total, panier.id)

    return redirect(redirect_url)
"""

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from store.domain.services import traiter_paiement_moncash_local
from datetime import date

@login_required
@require_POST
def paiement_moncash_local_ajax(request):
    numero = request.POST.get("numero")
    motpass = request.POST.get("motpass")
    adresse = request.POST.get("adresse")
    telephone = request.POST.get("telephone")
    date_livraison = request.POST.get("date_livraison")

    if date_livraison:
        date_livraison_obj = date.fromisoformat(date_livraison)

        if date_livraison_obj < date.today():
            return JsonResponse({
                "success": False,
                "message": "La date de livraison ne peut pas être antérieure à aujourd'hui."
            })

    try:
        # 1️⃣ Vérification compte + solde
        traiter_paiement_moncash_local(request.user, numero, motpass)

        # 2️⃣ Création commande + paiement
        commande, paiement = payer_panier(
            user=request.user,
            mode_paiement="MonCash",
            reference=numero,
            adresse=adresse,
            telephone=telephone,
            date_livraison=date_livraison
        )

        return JsonResponse({
            "success": True,
            "redirect_url": "/store/mes_commandes/"
        })

    except PaiementInvalideError as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })

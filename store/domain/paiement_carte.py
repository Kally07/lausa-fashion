# store/domain/paiement_carte.py
import requests
from django.conf import settings
from store.domain.exceptions import PaiementInvalideError

def _get_carte_token():
    """
    Obtenir un token d'authentification pour l'API Carte de Crédit.
    """
    url = f"{settings.CARTE_BASE_URL}/oauth/token"

    try:
        response = requests.post(
            url,
            auth=(settings.CARTE_CLIENT_ID, settings.CARTE_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        raise PaiementInvalideError(f"Erreur token Carte : {e}")

    return data.get("access_token")


def creer_paiement_carte(montant: float, order_id: str):
    """
    Crée un paiement Carte de Crédit et retourne l'URL de redirection.
    """
    token = _get_carte_token()

    url = f"{settings.CARTE_BASE_URL}/api/v1/create_payment"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "amount": float(montant),
        "orderId": str(order_id),
        "currency": "HTG",  # ou autre selon ton API
        "description": f"Commande #{order_id}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        raise PaiementInvalideError(f"Erreur création paiement Carte : {e}")

    redirect_url = data.get("redirect_url")
    if not redirect_url:
        raise PaiementInvalideError("Lien de redirection Carte manquant")

    return redirect_url


def valider_paiement_carte(reference: str, montant: float, use_transaction_id=False):
    """
    Valide un paiement Carte après la transaction.
    """
    token = _get_carte_token()

    url = f"{settings.CARTE_BASE_URL}/api/v1/validate_payment"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {"orderId": str(reference)} if not use_transaction_id else {"transactionId": str(reference)}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        raise PaiementInvalideError(f"Erreur validation paiement Carte : {e}")

    payment = data.get("payment")
    if not payment or payment.get("status") != "SUCCESS":
        raise PaiementInvalideError("Paiement Carte non validé")

    if float(payment.get("amount", 0)) != float(montant):
        raise PaiementInvalideError("Montant Carte incorrect")

    return True

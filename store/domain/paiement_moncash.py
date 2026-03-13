import requests
from django.conf import settings
from store.domain.exceptions import PaiementInvalideError


def _get_moncash_token():
    """
    Obtient le token OAuth2 MonCash pour l'API sandbox.
    """
    url = f"{settings.MONCASH_BASE_URL}/Api/oauth/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # ⚠️ Assure-toi que le scope correspond à ce que MonCash t'a fourni dans le portail sandbox
    payload = "grant_type=client_credentials&scope=PAYMENTS"

    try:
        response = requests.post(
            url,
            headers=headers,
            auth=(settings.MONCASH_CLIENT_ID, settings.MONCASH_CLIENT_SECRET),
            data=payload,
            timeout=30
        )

        # Debug temporaire
        print("=== MonCash OAuth ===")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()
        data = response.json()

    except requests.RequestException as e:
        raise PaiementInvalideError(
            f"Erreur lors de l'obtention du token MonCash: {e}"
        )

    token = data.get("access_token")
    if not token:
        raise PaiementInvalideError("Token MonCash non reçu")

    return token


def creer_paiement_moncash(montant: float, order_id: str):
    """
    Crée un paiement MonCash et retourne l'URL de redirection.
    """
    token = _get_moncash_token()

    url = f"{settings.MONCASH_BASE_URL}/Api/v1/CreatePayment"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "amount": float(montant),
        "orderId": str(order_id),
        # ⚠️ On peut ajouter des infos optionnelles comme description ou callback URL
        "returnUrl": settings.MONCASH_RETURN_URL,
        "cancelUrl": settings.MONCASH_CANCEL_URL,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        raise PaiementInvalideError(f"Erreur MonCash: {e}")

    # Debug temporaire
    print("=== MonCash CreatePayment ===")
    print("RESPONSE:", data)

    # Gestion flexible du redirect
    redirect_url = (
        data.get("redirectUrl")
        or data.get("redirect_url")
    )

    # Si API retourne payment_token
    if not redirect_url and "payment_token" in data:
        token_value = data["payment_token"].get("token")
        if token_value:
            redirect_url = f"{settings.MONCASH_BASE_URL}/Payment/Redirect?token={token_value}"

    if not redirect_url:
        raise PaiementInvalideError("Lien de redirection MonCash manquant")

    return redirect_url


def valider_paiement_moncash(reference: str, montant: float, use_transaction_id=False):
    """
    Valide qu'un paiement MonCash a été effectué pour une commande.
    """
    token = _get_moncash_token()

    url = f"{settings.MONCASH_BASE_URL}/Api/v1/RetrieveOrderPayment"
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
        raise PaiementInvalideError(f"Erreur lors de la validation du paiement MonCash: {e}")

    payment = data.get("payment")
    if not payment or payment.get("status") != "SUCCESS":
        raise PaiementInvalideError("Paiement MonCash non validé")

    if float(payment.get("amount", 0)) != float(montant):
        raise PaiementInvalideError("Montant MonCash incorrect")

    return True

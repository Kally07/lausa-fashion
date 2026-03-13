import requests
from django.conf import settings


class MonCashSDK:

    def __init__(self):
        self.base_url = settings.MONCASH_BASE_URL
        self.client_id = settings.MONCASH_CLIENT_ID
        self.client_secret = settings.MONCASH_CLIENT_SECRET

    def _get_token(self):
        url = f"{self.base_url}/Api/oauth/token"

        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            timeout=30
        )

        response.raise_for_status()
        return response.json()["access_token"]

    def create_payment(self, amount, order_id):
        token = self._get_token()

        url = f"{self.base_url}/Api/v1/CreatePayment"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "amount": amount,
            "orderId": order_id
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        return response.json()

    def get_payment_status(self, payment_id):
        token = self._get_token()

        url = f"{self.base_url}/Api/v1/RetrievePayment/{payment_id}"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        return response.json()

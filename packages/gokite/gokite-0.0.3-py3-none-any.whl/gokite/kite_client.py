import os
import requests
from typing import Optional
from .exceptions import KiteError, KiteAuthenticationError, KiteNetworkError, KiteNotFoundError

class KiteClient:
    """
    Kite SDK Client for interacting with Kite backend and blockchain layer.
    """

    DEFAULT_API_BASE_URL = "https://neo.staging.gokite.ai"  # Example base URL, replace with actual if different

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or os.environ.get("KITE_API_KEY")
        if not self.api_key:
            raise KiteAuthenticationError("Missing KITE_API_KEY")

        self.base_url = base_url or self.DEFAULT_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        # cache service details
        self._service_details = {}

    def make_payment(self, to_address: str, amount: float) -> str:
        """Make on-chain payment"""
        raise NotImplementedError("MakePayment is not implemented yet")

    def load_service_description(self, service_id: str) -> dict:
        url = f"{self.base_url}/v1/asset?"
        if service_id.startswith("agent_"):
            url += f"id={service_id}"
        else:
            url += f"name={service_id}"
        try:
            response = self.session.get(url)
        except Exception as e:
            raise KiteNetworkError(e)
        result = self._handle_response(response)
        if not result.get("data"):
            raise KiteError(f"Invalid response (status {response.status_code}): {result.get('error', response.text)}")
        return result["data"].get("description")

    def call_service(self, service_id: str, payload: dict) -> dict:
        # TODO: get deployment url from service_id
        url = "https://deployment-mjx99rerj0pviyq89xb0jcbi.prod.gokite.ai/main"
        try:
            response = requests.post(url, json=payload)
        except Exception as e:
            raise KiteNetworkError(e)
        result = self._handle_response(response)
        return result

    def _handle_response(self, response):
        """Handle HTTP response uniformly"""
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise KiteError("Invalid response from server")

        if 200 <= response.status_code < 300:
            return data
        
        if response.status_code == 401 or response.status_code == 403:
            raise KiteAuthenticationError(
                f"Authentication failed (status {response.status_code}): {data.get('error', response.text)}"
            )
        elif response.status_code == 404:
            raise KiteNotFoundError(
                f"Resource not found (status {response.status_code}): {data.get('error', response.text)}"
            )
        elif 400 <= response.status_code < 500:
            raise KiteError(
                f"Client error (status {response.status_code}): {data.get('error', response.text)}"
            )
        elif 500 <= response.status_code < 600:
            raise KiteError(
                f"Server error (status {response.status_code}): {data.get('error', response.text)}"
            )
        else:
            error_msg = data.get("error", "Unknown error")
            raise KiteError(error_msg)

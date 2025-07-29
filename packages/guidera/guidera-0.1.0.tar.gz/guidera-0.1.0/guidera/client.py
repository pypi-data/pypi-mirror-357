import requests
from typing import Optional, Dict, Any, List

class Client:
    """
    Client for interacting with the Tilantra Model Swap Router API.
    Usage:
        guidera_client = Client(auth_token)
        response = guidera_client.generate(prompt, prefs, cp_tradeoff_parameter)
        suggestions = guidera_client.get_suggestions(prompt)
    """
    def __init__(self, auth_token: str, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the client with an authentication token and API base URL.
        """
        self.auth_token = auth_token
        self.api_base_url = api_base_url.rstrip("/")

    @staticmethod
    def register_user(username: str, email: str, password: str, full_name: Optional[str] = None, company: Optional[str] = None, api_base_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """
        Register a new user. Returns the API response.
        """
        url = f"{api_base_url.rstrip('/')}/register"
        payload = {
            "username": username,
            "email": email,
            "password": password,
        }
        if full_name:
            payload["full_name"] = full_name
        if company:
            payload["company"] = company
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, 'response', None)}

    @staticmethod
    def generate_token(username: str, email: str, force_new: bool = False, api_base_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """
        Generate or retrieve a JWT token for a user. Returns the API response.
        """
        url = f"{api_base_url.rstrip('/')}/generate_token"
        payload = {
            "username": username,
            "email": email,
            "force_new": force_new
        }
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, 'response', None)}

    def generate(self, prompt: str, prefs: Optional[Dict[str, Any]] = None, cp_tradeoff_parameter: float = 0.7) -> Dict[str, Any]:
        """
        Generate a response from the model router.
        """
        url = f"{self.api_base_url}/generate"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "prompt": prompt,
            "prefs": prefs or {},
            "cp_tradeoff_parameter": cp_tradeoff_parameter
        }
        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, 'response', None)}

    def get_suggestions(self, prompt: str) -> Dict[str, Any]:
        """
        Get prompt suggestions from the model router.
        """
        url = f"{self.api_base_url}/suggestion"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {"prompt": prompt}
        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, 'response', None)} 
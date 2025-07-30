import requests
import json
from requests.auth import HTTPDigestAuth
from typing import Optional, Union

class DinstarUC:
    """
    Base class for interacting with the Dinstar API.
    This class handles authentication and sending HTTP requests.
    """

    def __init__(self, username, password, gateway_url, verify_ssl=True):
        """
        Initialize the DinstarUC class with authentication details.
        :param username: API username.
        :param password: API password.
        :param gateway_url: Base URL of the Dinstar gateway.
        :param verify_ssl: Whether to verify SSL certificates (default: True).
        """
        self.username = username
        self.password = password
        self.gateway_url = gateway_url
        self.verify_ssl = verify_ssl

    def send_api_request(
        self,
        endpoint: str,
        data: Optional[any] = None,
        method: str = "POST",
        raw: bool = False
    ) -> Optional[Union[dict, requests.Response]]:
        """
        Send an authenticated HTTP request to the Dinstar API.

        Args:
            endpoint (str): API endpoint to send the request to.
            data (any, optional): Request payload (dict for POST, query params for GET).
            method (str): HTTP method ("GET" or "POST"). Defaults to "POST".
            raw (bool): If True, return the full requests.Response object. Defaults to False.

        Returns:
            dict: Parsed JSON response if raw=False.
            requests.Response: Full HTTP response if raw=True.
            None: On failure.
        """
        url = f"{self.gateway_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            if method.upper() == "GET":
                response = requests.get(
                    url,
                    auth=HTTPDigestAuth(self.username, self.password),
                    headers=headers,
                    params=data,
                    verify=self.verify_ssl
                )
            elif method.upper() == "POST":
                body = data if isinstance(data, str) else json.dumps(data) if data else None
                response = requests.post(
                    url,
                    auth=HTTPDigestAuth(self.username, self.password),
                    headers=headers,
                    data=body,
                    verify=self.verify_ssl
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response if raw else response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request to {url} failed: {e}")
            return None

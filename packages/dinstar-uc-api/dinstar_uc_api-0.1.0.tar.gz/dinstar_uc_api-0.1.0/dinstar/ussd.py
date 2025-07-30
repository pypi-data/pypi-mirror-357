from dinstar.base import DinstarUC
from typing import List, Optional
from .models import DinstarApiResponse, DinstarUSSDReply, DinstarUSSDResult

class DinstarUSSD(DinstarUC):
    """
    Class for handling USSD operations using the Dinstar API.
    """

    def send_ussd(
            self,
            text: str,
            ports: List[int],
            command: Optional[str] = "send"
    ) -> DinstarApiResponse[List[DinstarUSSDResult]]:
        """
        Send a USSD message to one or more ports.

        Args:
            text (str): USSD code or message to send (max 60 bytes).
                        Required if command is "send".
            ports (List[int]): List of port numbers (0–31) to send the message through.
            command (Optional[str]): "send" (default) or "cancel".

        Returns:
            DinstarApiResponse[List[DinstarUSSDResult]]: List of USSD sending results per port.

        Example:
            {
                "port": [1, 2, 3],
                "command": "send",
                "text": "*125#"
            }

        Response contains result list per port with status codes:
            - 200: USSD sent successfully
            - 486: Port is busy
            - 503: Port not registered
        """
        endpoint = "/api/send_ussd"
        payload = {
            "text": text,
            "port": ports,
            "command": command
        }

        response = self.send_api_request(endpoint, data=payload)
        error_code = response.get("error_code")
        sn = response.get("sn")
        raw_results = response.get("result", [])
        data = [DinstarUSSDResult(**item) for item in raw_results] if error_code == 202 else None
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)

    def query_ussd_reply(self, ports: List[int]) -> DinstarApiResponse[List[DinstarUSSDReply]]:
        """
        Query the latest USSD reply received by the given ports.

        Args:
            ports (List[int]): List of port numbers (0–31) to query.

        Returns:
            DinstarApiResponse[List[DinstarUSSDReply]]: List of USSD replies per port.

        Example:
            /api/query_ussd_reply?port=1,2,3

        Response includes:
            - error_code: status of the request
            - sn: gateway serial number
            - reply: list of USSD replies per port
        """
        endpoint = "/api/query_ussd_reply"
        params = {
            "port": ",".join(str(p) for p in ports)
        }

        response = self.send_api_request(endpoint, data=params, method="GET")
        error_code = response.get("error_code")
        sn = response.get("sn")
        raw_reply = response.get("reply", [])
        data = [DinstarUSSDReply(**item) for item in raw_reply] if error_code == 200 else None
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)
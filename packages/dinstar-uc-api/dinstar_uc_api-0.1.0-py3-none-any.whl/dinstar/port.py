from dinstar.base import DinstarUC
from typing import List, Optional
from .models import DinstarApiResponse, DinstarPortInfo

class DinstarPort(DinstarUC):
    """
    Class for handling port-related operations using the Dinstar API.
    """

    def get_port_info(
            self,
            info_type: List[str],
            ports: Optional[List[int]] = None,
    ) -> DinstarApiResponse[List[DinstarPortInfo]]:
        """
        Get detailed port information from the Dinstar gateway.

        Args:
            info_type (List[str]): List of information types to query.
            ports (Optional[List[int]]): Specific ports to query (0–31). If omitted, all ports are queried.

        Returns:
            DinstarApiResponse[List[DinstarPortInfo]]: Parsed port information for each queried port.

        Example request:
            /api/get_port_info?port=1,2,3&info_type=imei,imsi,iccid,...

        Example response:
            {
                "error_code": 200,
                "sn": "xxxx-xxxx-xxxx-xxxx",
                "info": [
                    {
                        "port": 1,
                        "type": "WCDMA",
                        "imei": "863070017005173",
                        ...
                    }
                ]
            }
        """
        endpoint = "/api/get_port_info"
        params = {
            "info_type": ",".join(info_type)
        }
        if ports:
            params["port"] = ",".join(str(p) for p in ports)

        response = self.send_api_request(endpoint, data=params, method="GET")
        error_code = response.get("error_code")
        sn = response.get("sn")
        raw_info = response.get("info", [])
        data = [DinstarPortInfo(**item) for item in raw_info] if error_code == 200 else None
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)

    def set_port_info(
            self,
            port: int,
            action: str,
            param: str,
    ) -> DinstarApiResponse[None]:
        """
        Perform an action on a specific port, such as power control, SIM operations, or slot selection.

        Args:
            port (int): Port number (0–31).
            action (str): Action to perform. Valid values include:
                          "slot", "reset", "power", "imei", "number", "lock", "unlock",
                          "block", "unblock", "CallForward", "CheckCallForward".
            param (str): Action-specific parameter value, such as slot number, PIN, "on"/"off", etc.

        Returns:
            DinstarApiResponse[None]: Response containing error_code and SN if successful.

        Example:
            /api/set_port_info?port=1&action=power&param=off
        """
        endpoint = "/api/set_port_info"
        params = {
            "port": port,
            "action": action,
            "param": param
        }

        response = self.send_api_request(endpoint, data=params, method="GET")
        error_code = response.get("error_code")
        sn = response.get("sn")
        return DinstarApiResponse(error_code=error_code, sn=sn, data=None)

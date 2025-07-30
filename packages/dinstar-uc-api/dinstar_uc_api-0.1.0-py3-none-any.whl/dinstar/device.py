from dinstar.base import DinstarUC
from .models import DinstarDeviceStatus
from typing import Optional

class DinstarDevice(DinstarUC):
    """
    Class for handling device status operations using the Dinstar API.
    """

    def get_device_status(self) -> Optional[DinstarDeviceStatus]:
        """
        POST: Get performance metrics from the Dinstar device.

        Returns:
            [DinstarDeviceStatus]: API response wrapper containing performance data.

        Response example:
        {
            "performance": {
                "cpu_used": "39",
                "flash_total": "27648",
                "flash_used": "17428",
                "memory_total": "109448",
                "memory_cached": "34192",
                "memory_buffers": "0",
                "memory_free": "58928",
                "memory_used": "50520"
            }
        }
        """
        endpoint = "/api/get_status"
        data = '["performance"]'
        # Send the JSON array as a string
        response = self.send_api_request(endpoint, data, method="POST",raw=True)

        if response is None or response.status_code != 200:
            return None

        json_data = response.json()
        performance_info = json_data.get("performance")
        if not performance_info:
            return None

        return DinstarDeviceStatus(**performance_info)
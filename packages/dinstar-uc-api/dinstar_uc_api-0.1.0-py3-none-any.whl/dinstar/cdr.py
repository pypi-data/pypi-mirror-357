from dinstar.base import DinstarUC

from typing import List, Optional
from .models import DinstarCDRRecord, DinstarApiResponse

class DinstarCDR(DinstarUC):
    def get_cdr(
        self,
        ports: Optional[List[int]] = None,
        time_after: Optional[str] = None,
        time_before: Optional[str] = None,
    ) -> DinstarApiResponse[List[DinstarCDRRecord]]:
        """
        POST: Get call detail records (CDR) from the Dinstar gateway.

        Args:
            ports (Optional[List[int]]): List of port numbers to filter (0-31).
            time_after (Optional[str]): Filter for CDRs after this time (format "YYYY-MM-DD HH:MM:SS").
            time_before (Optional[str]): Filter for CDRs before this time (format "YYYY-MM-DD HH:MM:SS").

        Returns:
            DinstarApiResponse[List[DinstarCDRRecord]]: API response wrapper containing CDR records.

        Response:
            {
                "error_code": 200,
                "sn": "xxxx-xxxx-xxxx-xxxx",
                "cdr": [
                    {
                        "port": 2,
                        "start_date": "2015-07-21 16:35:20",
                        "answer_date": "2015-07-21 16:35:31",
                        "duration": 3,
                        "source_number": "1010",
                        "destination_number": "6717",
                        "direction": "ip->gsm",
                        "ip": "172.16.100.136",
                        "codec": "G.711U",
                        "hangup": "called",
                        "gsm_code": 16,
                        "bcch": ""
                    }
                ]
            }
        """
        endpoint = "/api/get_cdr"
        data = {}
        if ports:
            data["port"] = ports
        if time_after:
            data["time_after"] = time_after
        if time_before:
            data["time_before"] = time_before

        response_json = self.send_api_request(endpoint, data)
        error_code = response_json.get("error_code")
        sn = response_json.get("sn")
        raw_cdrs = response_json.get("cdr", [])
        data = [DinstarCDRRecord(**cdr) for cdr in raw_cdrs] if error_code == 200 else None
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)

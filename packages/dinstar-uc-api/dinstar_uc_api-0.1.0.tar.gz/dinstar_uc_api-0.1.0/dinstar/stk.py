from dinstar.base import DinstarUC
from .models import DinstarSTKView, DinstarSTKItem, DinstarApiResponse
from typing import Optional

class DinstarSTK(DinstarUC):
    """
    Class for handling SIM Toolkit (STK) operations using the Dinstar API.
    """

    def query_stk_info(self, port: int) -> Optional[DinstarSTKView]:
        """
        Retrieve the current STK (SIM Toolkit) view information for a specific port.

        Args:
            port (int): Port number to query (0–31).

        Returns:
            Optional[DinstarSTKView]: STK view info including menu items, prompts, etc.

        Example request:
            /GetSTKView?port=0

        Example response:
            {
                "title": "STK MENU",
                "item": [{"item_id": 1, "item_string": "item1_text"}, ...],
                "input_type": 2,
                "frame_id": 750
            }
        """
        endpoint = "/GetSTKView"
        params = {"port": port}

        response = self.send_api_request(endpoint, data=params, method="GET", raw=True)
        if not response:
            return None
        print(response.content)

        raw = response.json()
        item_list = [DinstarSTKItem(**i) for i in raw.get("item", [])]

        return DinstarSTKView(
            title=raw.get("title"),
            text=raw.get("text"),
            input_type=int(raw["input_type"]),
            frame_id=int(raw["frame_id"]),
            item=item_list or None
        )

    def send_stk_reply(
            self,
            port: int,
            item: Optional[int] = None,
            param: Optional[str] = None,
            action: Optional[str] = None
    ) -> DinstarApiResponse[None]:
        """
        Send a reply or selection to the STK (SIM Toolkit) interface.

        Args:
            port (int): Port number (0–31) to target.
            item (Optional[int]): Selected menu item ID, if applicable.
            param (Optional[str]): Input value (e.g. USSD, PIN, or other typed input).
            action (Optional[str]): One of "ok", "cancle" (yes, it's misspelled), or "home".

        Returns:
            DinstarApiResponse[None]: Result of the STK operation with error code and SN.

        Example:
            {
                "port": 0,
                "action": "cancle"
            }
        """
        endpoint = "/STKGo"
        payload = {"port": port}
        if item is not None:
            payload["item"] = item
        if param is not None:
            payload["param"] = param
        if action is not None:
            payload["action"] = action

        response = self.send_api_request(endpoint, data=payload)
        return DinstarApiResponse(
            error_code=response.get("error_code"),
            sn=response.get("sn"),
            data=None
        )

    def get_stk_frame_id(self, port: int) -> Optional[int]:
        """
        Get the current STK frame ID for the given port.

        Args:
            port (int): Port number (0–31).

        Returns:
            Optional[int]: The current frame ID if successful, or None if failed.

        Example:
            /GetSTKCurrFrameIndex?port=0

        Response:
            {
                "frame_id": 32
            }
        """
        endpoint = "/GetSTKCurrFrameIndex"
        params = {"port": port}

        response = self.send_api_request(endpoint, data=params, method="GET", raw=True)
        if not response:
            return None

        return int(response.json()["frame_id"]) or None
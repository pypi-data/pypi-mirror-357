from dinstar.base import DinstarUC

from .models import (
    DinstarApiResponse,
    DinstarSMSReceiveMessage,
    DinstarSendSMSResponse,
    DinstarStopSMSTaskResponse,
    DinstarSMSResult,
    DinstarSMSDeliveryStatus,
    DinstarSMSQueueStatus,
)

from typing import List, Optional
from pydantic import BaseModel, Field

class DinstarSMSMessage(BaseModel):
    """
    Represents a single SMS message to be sent.

    Attributes:
        text (str): The content of the SMS message.
        number (str): Number of the person who we want to send the message
        port (list[int] | None): Optional. Port which we want to send via
        encoding (str): Encoding type, either 'unicode' or 'gsm-7bit' (default: 'unicode').
        request_status_report (bool): Whether to request SMS delivery status report (default: True).
    """
    text: str
    number: str
    port: Optional[List[int]] = None
    encoding: Optional[str] = Field(default="unicode")
    request_status_report: Optional[bool] = Field(default=True)
    user_id: Optional[int] = None

class DinstarBatchSMS(BaseModel):
    """
    Represents a batch of SMS messages to be sent in a single API call.

    Attributes:
        messages (List[DinstarSMSMessage]): List of SMS messages in the batch.
            The batch size is limited to a maximum of 50 messages.
    """
    messages: List[DinstarSMSMessage]

    def __init__(self, **data):
        super().__init__(**data)
        if len(self.messages) > 50:
            raise ValueError("Maximum 50 messages allowed in a batch")

class DinstarSMS(DinstarUC):
    def send_sms(self, batch: DinstarBatchSMS) -> DinstarApiResponse[DinstarSendSMSResponse]:
        """
        Send an SMS message to one or multiple recipients.

        Args:
            DinstarBatchSMS - a SMS batch to be sent.

        Returns:
            dict: JSON response from the API containing:
                - error_code (int): Status code, e.g., 200 for accepted.
                - sn (str): Serial number of the gateway.
                - sms_in_queue (int): Number of SMS messages waiting to be processed.
                - task_id (int): ID of the SMS sending task.

        Example:
            Simple request payload:
            {
                "text": "ye",
                "param": [{"number": "10086"}]
            }

            Complex request payload with text_param and multiple ports:
            {
                "text": "#param#",
                "port": [2, 3],
                "param": [
                    {"number": "10086", "text_param": ["bj"], "user_id": 1},
                    {"number": "10086", "text_param": ["ye"], "user_id": 2}
                ]
            }

            Example response:
            {
                "error_code": 202,
                "sn": "xxxx-xxxx-xxxx-xxxx",
                "sms_in_queue": 2,
                "task_id": 2
            }
        """
        messages = batch.messages

        if len(messages) == 1:
            # Simple format
            msg = messages[0]
            payload = {
                "text": msg.text,
                "param": [{"number": msg.number}],
                "encoding": msg.encoding,
                "request_status_report": msg.request_status_report
            }
            if msg.port:
                payload["port"] = msg.port

        else:
            # Complex format
            payload = {
                "text": "#param#",
                "param": [],
                "encoding": messages[0].encoding,
                "request_status_report": messages[0].request_status_report
            }
            ports_set = set()
            for msg in messages:
                param_obj = {"number": msg.number}
                param_obj["text_param"] = [msg.text]
                if msg.user_id is not None:
                    param_obj["user_id"] = msg.user_id
                payload["param"].append(param_obj)
                if msg.port:
                    ports_set.update(msg.port)

            if ports_set:
                payload["port"] = sorted(ports_set)

        endpoint = "/api/send_sms"
        response_json = self.send_api_request(endpoint, payload)
        error_code = response_json.get("error_code")
        sn = response_json.get("sn")
        data = None
        if error_code == 200:
            data = DinstarSendSMSResponse(
                error_code=error_code,
                sn=sn,
                sms_in_queue=response_json.get("sms_in_queue", 0),
                task_id=response_json.get("task_id", 0),
            )
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)

    def get_sms_result(
        self,
        user_ids: Optional[List[int]] = None,
        numbers: Optional[List[str]] = None,
        ports: Optional[List[int]] = None,
        time_after: Optional[str] = None,
        time_before: Optional[str] = None,
    ) -> DinstarApiResponse[List[DinstarSMSResult]]:
        """
            Query SMS sending results from the Dinstar gateway.

            Args:
                numbers (list[str], optional): Array of recipient numbers.
                    The number of strings should not exceed 32, and each string's length should not exceed 24 bytes.
                ports (list[int], optional): Array of ports for sending SMS.
                    Each port should be an integer from 0 to 31.
                time_after (str, optional): Query records of SMS messages sent after this time, format "YYYY-MM-DD HH:MM:SS".
                time_before (str, optional): Query records of SMS messages sent before this time, format "YYYY-MM-DD HH:MM:SS".
                user_ids (list[int], optional): Array of user IDs used to match the user ID in Send SMS requests.
                    This unique value is set during sending SMS and is recommended for production use.
            Returns:
                dict: JSON response containing:
                    - error_code (int): Status code (e.g., 200 for success).
                    - sn (str): Serial number of the gateway.
                    - result (list of dict): List of SMS sending result entries, each containing:
                        - port (int)
                        - user_id (int)
                        - number (str)
                        - time (str)
                        - status (str)
                        - count (int)
                        - succ_count (int)
                        - ref_id (int)
                        - imsi (str)

            Example:
                Request:
                    {
                        "user_id": [1, 2]
                    }

                Response:
                    {
                        "error_code": 200,
                        "sn": "xxxx-xxxx-xxxx-xxxx",
                        "result": [
                            {
                                "port": 0,
                                "user_id": 1,
                                "number": "12351",
                                "time": "2014-12-21 12:06:01",
                                "status": "SENT_OK",
                                "count": 3,
                                "succ_count": 3,
                                "ref_id": 12,
                                "imsi": "460004642148063"
                            }
                        ]
                    }
            """
        endpoint = "/api/query_sms_result"
        data = {}
        if user_ids:
            data["user_id"] = user_ids
        if numbers:
            data["number"] = numbers
        if ports:
            data["port"] = ports
        if time_after:
            data["time_after"] = time_after
        if time_before:
            data["time_before"] = time_before
        response_json = self.send_api_request(endpoint, data)
        error_code = response_json.get("error_code")
        sn = response_json.get("sn")
        raw_results = response_json.get("result", [])
        data = [DinstarSMSResult(**item) for item in raw_results] if error_code == 200 else None
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)

    def get_sms_delivery_status(
        self,
        numbers: Optional[List[str]] = None,
        ports: Optional[List[int]] = None,
        time_after: Optional[str] = None,
        time_before: Optional[str] = None,
    ) -> DinstarApiResponse[List[DinstarSMSDeliveryStatus]]:
        """
        Query delivery status of sent SMS messages from the Dinstar gateway.

        Args:
            numbers (list[str], optional): Recipient numbers. Max 32 numbers, each max 24 bytes.
            ports (list[int], optional): Ports used for sending SMS. Integers 0-31.
            time_after (str, optional): Query SMS sent after this timestamp (YYYY-MM-DD HH:MM:SS).
            time_before (str, optional): Query SMS sent before this timestamp (YYYY-MM-DD HH:MM:SS).

        Returns:
            list[DinstarSMSDeliveryStatus]: List of SMS delivery status records, each containing:
                - port (int): Port used for sending SMS.
                - number (str): Destination number.
                - time (str): Time of sending.
                - ref_id (int): Reference ID used to match SMS sending result.
                - status_code (int): Delivery status code (0=received, 32-63=temporary error, 64-255=permanent error).
                - imsi (str): IMSI of the SIM card.

        Example:
            Request:
            {
                "number": ["12341234"],
                "port": [1, 2, 3],
                "time_after": "2014-12-12 19:29:19",
                "time_before": "2014-12-12 19:29:19"
            }

            Response:
            {
                "error_code": 200,
                "sn": "xxxx-xxxx-xxxx-xxxx",
                "result": [
                    {
                        "port": 0,
                        "number": "12341234",
                        "time": "2014-12-21 12:06:01",
                        "ref_id": 12,
                        "status_code": 0,
                        "imsi": "460004642148063"
                    }
                ]
            }
        """
        endpoint = "/api/query_sms_deliver_status"
        data = {}
        if numbers:
            data["number"] = numbers
        if ports:
            data["port"] = ports
        if time_after:
            data["time_after"] = time_after
        if time_before:
            data["time_before"] = time_before
        response_json = self.send_api_request(endpoint, data)
        error_code = response_json.get("error_code")
        sn = response_json.get("sn")
        raw_results = response_json.get("result", [])
        data = [DinstarSMSDeliveryStatus(**item) for item in raw_results] if error_code == 200 else None
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)

    def get_sms_queue(self) -> DinstarApiResponse[DinstarSMSQueueStatus]:
        """
        Query the current SMS queue status on the Dinstar gateway.

        Returns:
            DinstarSMSQueueStatus: Contains error code, gateway serial number,
            and number of SMS messages waiting to be sent.

        Example Response:
            {
                "error_code": 200,
                "sn": "xxxx-xxxx-xxxx-xxxx",
                "in_queue": 0
            }
        """
        endpoint = "/api/query_sms_queue"
        response_json = self.send_api_request(endpoint, {})
        error_code = response_json.get("error_code")
        sn = response_json.get("sn")
        data = None
        if error_code == 200:
            data = DinstarSMSQueueStatus(in_queue=response_json.get("in_queue", 0))
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)

    def get_sms(
            self,
            incoming_sms_id: Optional[int] = 0,
            flag: Optional[str] = "unread",
            ports: Optional[List[int]] = None,
    ) -> DinstarApiResponse[List[DinstarSMSReceiveMessage]]:
        """
         Retrieve incoming SMS messages from the Dinstar gateway.

         Args:
             incoming_sms_id (int): Optional. Default = 0. Only fetch messages with an ID greater than this value.
                 Useful for polling new messages incrementally.
             flag (str): Optional. Filter messages by status. Options:
                 - 'unread' (default): Only unread messages.
                 - 'read': Only read messages.
                 - 'all': All messages.
             ports (list[int] or None): Optional list of port numbers to filter messages by.

         Returns:
             dict: A JSON response with the following structure:
                 {
                     "error_code": 200,
                     "sn": "gateway-serial-number",  # Serial number of the gateway
                     "sms": [
                         {
                             "incoming_sms_id": 123,
                             "port": 1,
                             "number": "+1234567890",       # Sender's phone number
                             "smsc": "+1987654321",          # SMS center number
                             "timestamp": "2025-01-01 12:34:56",
                             "text": "Sample SMS message content.",
                             "imsi": "310260123456789"
                         },
                         ...
                     ],
                     "read": 4,    # Count of read messages
                     "unread": 2   # Count of unread messages
                 }

         Notes:
             - error_code 200 means success. 500 indicates a failure.
             - The response may be empty or contain multiple messages.
             - This method returns the raw JSON response.
               To convert messages into structured Python objects, wrap with a dataclass or parser.
         """
        endpoint = "/api/query_incoming_sms"
        data = {"incoming_sms_id": incoming_sms_id, "flag": flag}
        if ports:
            data["port"] = ports
        response_json = self.send_api_request(endpoint, data)
        error_code = response_json.get("error_code")
        sn = response_json.get("sn")
        raw_messages = response_json.get("sms", [])
        data = [DinstarSMSReceiveMessage.from_dict(msg) for msg in raw_messages] if error_code == 200 else None
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)

    def stop_sms(self, task_id: int) -> DinstarApiResponse[DinstarStopSMSTaskResponse]:
        """
        Stop an SMS sending task on the Dinstar gateway.

        Args:
            task_id (int): The ID of the SMS sending task to stop. This ID is
                obtained from the response of a previous SMS sending request.

        Returns:
            dict: JSON response from the API containing:
                - error_code (int): Status code of the operation:
                    - 200: SMS sending task has been stopped successfully.
                    - 404: SMS sending task not found.
                    - 500: Other errors.
                - sn (str): Serial number of the gateway.

        Example:
            Request:
                GET https://gateway_ip/api/stop_sms?task_id=1

            Response:
                {
                    "error_code": 200,
                    "sn": "xxxx-xxxx-xxxx-xxxx"
                }
        """
        endpoint = f"/api/stop_sms?task_id={task_id}"
        response_json = self.send_api_request(endpoint, {})
        error_code = response_json.get("error_code")
        sn = response_json.get("sn")
        data = None
        if error_code == 200:
            data = DinstarStopSMSTaskResponse(error_code=error_code, sn=sn)
        return DinstarApiResponse(error_code=error_code, sn=sn, data=data)
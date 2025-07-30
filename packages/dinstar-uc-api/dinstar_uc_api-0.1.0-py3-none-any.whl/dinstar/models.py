from dataclasses import dataclass
from typing import Generic, Optional, TypeVar, List

T = TypeVar("T")

@dataclass
class DinstarApiResponse(Generic[T]):
    """
    Generic API response wrapper for Dinstar API calls.

    This class encapsulates the standard metadata returned by
    the Dinstar API together with the typed payload data.

    Attributes:
        error_code (int): The status code returned by the API.
            Common codes:
            - 200: Request processed successfully
            - 400: Bad request format
            - 500: Internal server error or other errors
        sn (str): The serial number of the Dinstar gateway device.
        data (Optional[T]): The typed response data payload on success,
            or None if the request failed or returned no data.

    Usage:
        response = client.query_sms_result(...)
        if response.error_code == 200 and response.data:
            for item in response.data:
                print(item)
    """
    error_code: int
    sn: str
    data: Optional[T] = None

# --- Dinstar CDR datamodels ---

@dataclass
class DinstarCDRRecord:
    """
    Represents a Call Detail Record (CDR) from the Dinstar gateway.

    Attributes:
        port (int): Port number associated with the call.
        start_date (str): Call start time in 'YYYY-MM-DD HH:MM:SS' format.
        answer_date (str): Call answer time in 'YYYY-MM-DD HH:MM:SS' format.
        duration (int): Duration of the call in seconds.
        source_number (str): Number of the calling party.
        destination_number (str): Number of the called party.
        direction (str): Call direction (e.g., 'gsm->ip', 'ip->gsm', 'callback').
        ip (str): Source IP address for IP to GSM calls.
        codec (str): Codec used for the call (e.g., 'G.711U', 'G.723.1').
        hangup (str): Which party hung up ('called', 'calling', or 'gateway').
        gsm_code (int): GSM reason code for call hangup.
        bcch (str): Broadcast Control Channel information used during the call.
    """
    port: int
    start_date: str
    answer_date: str
    duration: int
    source_number: str
    destination_number: str
    direction: str
    ip: str
    codec: str
    hangup: str
    gsm_code: int
    bcch: str

# --- Dinstar device datamodels ---

@dataclass
class DinstarDeviceStatus:
    """
    Represents device performance and status information reported by the Dinstar gateway.

    Attributes:
        cpu_used (str): CPU usage percentage.
        flash_total (str): Total flash memory size.
        flash_used (str): Used flash memory size.
        memory_total (str): Total memory size.
        memory_cached (str): Cached memory size.
        memory_buffers (str): Memory used for buffers.
        memory_free (str): Free memory size.
        memory_used (str): Used memory size.
    """
    cpu_used: str
    flash_total: str
    flash_used: str
    memory_total: str
    memory_cached: str
    memory_buffers: str
    memory_free: str
    memory_used: str

# --- Dinstar port datamodels ---

@dataclass
class DinstarPortInfo:
    """
    Represents detailed information for a specific port on the Dinstar gateway.

    Attributes:
        port (int): Port number (0–31).
        type (str): Network type (e.g., GSM, CDMA, WCDMA, LTE, UNKNOWN).
        imei (str): IMEI of the modem.
        imsi (str): IMSI of the inserted SIM card.
        iccid (str): ICCID of the SIM card.
        number (str): Mobile number associated with the SIM.
        reg (str): Registration status (e.g., REGISTER_OK, NO_SIM, UNREGISTER).
        slot (int): SIM slot index; 255 if not applicable.
        callstate (str): Call state (e.g., Idle, Active, Ringing).
        signal (int): Signal strength (0–31).
        gprs (str): GPRS attachment status (e.g., attached, detached).
        remain_credit (str): Total remaining credit.
        remain_monthly_credit (str): Monthly remaining credit.
        remain_daily_credit (str): Daily remaining credit.
        remain_daily_call_time (str): Remaining call time for the day.
        remain_hourly_call_time (str): Remaining call time for the hour.
        remain_daily_connected (str): Remaining daily call connection count.
    """
    port: int
    type: str
    imei: str
    imsi: str
    iccid: str
    number: str
    reg: str
    slot: int
    callstate: str
    signal: int
    gprs: str
    remain_credit: str
    remain_monthly_credit: str
    remain_daily_credit: str
    remain_daily_call_time: str
    remain_hourly_call_time: str
    remain_daily_connected: str

# --- Dinstar SMS datamodels ---

@dataclass
class DinstarSendSMSResponse:
    """
    Response returned after sending an SMS.

    Attributes:
        error_code (int): Status code indicating the result of the send operation.
        sn (str): Serial number of the gateway.
        sms_in_queue (int): Number of SMS messages waiting in the queue.
        task_id (int): Identifier for the SMS sending task.
    """
    error_code: int
    sn: str
    sms_in_queue: int
    task_id: int

@dataclass
class DinstarSMSResult:
    """
    Represents the result of an SMS sending operation.

    Attributes:
        port (int): Port used to send the SMS.
        user_id (int): Unique user ID assigned to the SMS.
        number (str): Recipient phone number.
        time (str): Timestamp of the send operation.
        status (str): Status of the SMS sending process.
        count (int): Number of SMS segments sent.
        succ_count (int): Number of SMS segments sent successfully.
        ref_id (int): Reference ID used to match delivery status.
        imsi (str): IMSI of the SIM card.
    """
    port: int
    user_id: int
    number: str
    time: str
    status: str
    count: int
    succ_count: int
    ref_id: int
    imsi: str

@dataclass
class DinstarSMSDeliveryStatus:
    """
    Represents the delivery status of a sent SMS.

    Attributes:
        port (int): Port used to send the SMS.
        number (str): Recipient phone number.
        time (str): Timestamp when the delivery status was reported.
        ref_id (int): Reference ID to match delivery status.
        status_code (int): Delivery status code (0 = received, 32-63 = temporary error, 64-255 = permanent error).
        imsi (str): IMSI of the SIM card.
    """
    port: int
    number: str
    time: str
    ref_id: int
    status_code: int
    imsi: str

@dataclass
class DinstarSMSQueueStatus:
    """
    Represents the status of the SMS queue in the gateway.

    Attributes:
        error_code (int): Status code of the queue query operation.
        sn (str): Serial number of the gateway.
        in_queue (int): Number of SMS messages waiting in the queue.
    """
    error_code: int
    sn: str
    in_queue: int

@dataclass
class DinstarSMSReceiveMessage:
    """
    Represents an incoming SMS message retrieved from the Dinstar gateway.

    Attributes:
        incoming_sms_id (int): Unique identifier for the incoming SMS.
        port (int): Port number that received the SMS.
        number (str): Sender's phone number.
        smsc (str): SMS center number.
        timestamp (str): Timestamp when the SMS was received.
        text (str): Content of the SMS message.
        imsi (str): IMSI of the SIM card.
    """
    incoming_sms_id: int
    port: int
    number: str
    smsc: str
    timestamp: str
    text: str
    imsi: str

    @staticmethod
    def from_dict(data: dict) -> "DinstarSMSReceiveMessage":
        return DinstarSMSReceiveMessage(
            incoming_sms_id=data.get("incoming_sms_id", 0),
            port=data.get("port", -1),
            number=data.get("number", ""),
            smsc=data.get("smsc", ""),
            timestamp=data.get("timestamp", ""),
            text=data.get("text", ""),
            imsi=data.get("imsi", "")
        )

@dataclass
class DinstarStopSMSTaskResponse:
    """
    Response returned after stopping an SMS sending task.

    Attributes:
        error_code (int): Status code indicating the result of the stop operation.
        sn (str): Serial number of the gateway.
    """
    error_code: int
    sn: str

# --- Dinstar STK dataclasses ---

@dataclass
class DinstarSTKItem:
    """
    Represents a selectable STK menu item.

    Attributes:
        item_id (int): The ID of the menu item.
        item_string (str): The label or name of the menu item.
    """
    item_id: int
    item_string: str


@dataclass
class DinstarSTKView:
    """
    Represents the current STK interface view returned by the gateway.

    Attributes:
        title (str): Title of the STK menu or view.
        text (Optional[str]): Optional prompt or description text.
        input_type (int): Defines the type of interaction required (e.g., display, select, input).
        frame_id (int): Frame ID of the current STK view.
        item (Optional[List[DinstarSTKItem]]): List of menu items (if applicable).
    """
    title: Optional[str]
    text: Optional[str]
    input_type: int
    frame_id: int
    item: Optional[List[DinstarSTKItem]] = None

# --- Dinstar USSD dataclasses ---

@dataclass
class DinstarUSSDResult:
    """
    Represents the result of a USSD send attempt for a specific port.

    Attributes:
        port (int): Port number the USSD was sent from.
        status (int): Status code of the USSD operation.
                      - 200: Sent successfully
                      - 486: Port is busy
                      - 503: Port is not registered
    """
    port: int
    status: int

@dataclass
class DinstarUSSDReply:
    """
    Represents a USSD reply received from a specific port.

    Attributes:
        port (int): Port number that received the USSD reply.
        text (str): The content of the USSD reply.
    """
    port: int
    text: str
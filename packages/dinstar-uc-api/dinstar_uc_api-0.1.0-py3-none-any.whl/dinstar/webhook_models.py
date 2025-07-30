# --- Push Event Models ---
"""
Webhook event models for Dinstar push notifications.

These Pydantic models define the structure of payloads
received from the gateway via webhook HTTP POST requests.
"""

from pydantic import BaseModel
from typing import List, Optional


# --- Item Classes ---

class PushSMS(BaseModel):
    """
    Represents a single incoming SMS message.

    Example:
    {
        "incoming_sms_id": 1,
        "port": 1,
        "number": "6717",
        "smsc": "+8613800757511",
        "timestamp": "2016-07-12 15:46:18",
        "text": "test"
    }
    """
    incoming_sms_id: int
    port: int
    number: str
    smsc: str
    timestamp: str
    text: str


class PushSMSResult(BaseModel):
    """
    Represents a single SMS sending result entry.

    Example:
    {
        "port": 1,
        "number": "10086",
        "time": "2016-07-12 15:46:18",
        "status": "DELIVERED",
        "count": 1,
        "succ_count": 1,
        "ref_id": 212,
        "imsi": "460004642148063"
    }
    """
    port: int
    number: str
    time: str
    status: str
    count: int
    succ_count: int
    ref_id: int
    imsi: str


class PushSMSDeliveryStatus(BaseModel):
    """
    Represents a single SMS delivery status entry.

    Example:
    {
        "port": 1,
        "number": "10082",
        "time": "2016-07-12 15:46:18",
        "ref_id": 212,
        "status_code": 0,
        "imsi": "460004642148063"
    }
    """
    port: int
    number: str
    time: str
    ref_id: int
    status_code: int
    imsi: str


class PushUSSD(BaseModel):
    """
    Represents a single USSD message entry.

    Example:
    {
        "port": 1,
        "text": "Thank"
    }
    """
    port: int
    text: str


class PushSIMRegister(BaseModel):
    """
    Represents a single SIM register status entry.

    Example:
    {
        "port": 8,
        "iccid": "8986004019184471023",
        "imsi": "460004642148063",
        "number": "13714637674",
        "status": "up",
        "sequence": 2,
        "slot": 2
    }
    """
    port: int
    iccid: Optional[str]
    imsi: Optional[str]
    number: Optional[str]
    status: str
    sequence: int
    slot: int


class PushCDR(BaseModel):
    """
    Represents a single call detail record (CDR) entry.

    Example:
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


class PushDevice(BaseModel):
    """
    Represents device status information.

    Example:
    {
        "port_number": 32,
        "IP": "172.18.55.142",
        "MAC": "F8-A0-3D-48-E5-19",
        "status": "power_off"
    }
    """
    port_number: int
    IP: str
    MAC: str
    status: str


class PushExceptionInfo(BaseModel):
    """
    Represents exception information.

    Example:
    {
        "port": 0,
        "type": "call_fail",
        "action": "reset"
    }
    """
    port: int
    type: str
    action: str


# --- Wrapper Webhook Payload Classes ---

class PushSMSWebhook(BaseModel):
    """
    Webhook payload containing incoming SMS messages.

    Attributes:
        sn (str): Serial number of the gateway device.
        sms (List[PushSMS]): List of incoming SMS messages.
    """
    sn: str
    sms: List[PushSMS]


class PushSMSResultWebhook(BaseModel):
    """
    Webhook payload containing SMS sending results.

    Attributes:
        sn (str): Serial number of the gateway device.
        sms_result (List[PushSMSResult]): List of SMS sending results.
    """
    sn: str
    sms_result: List[PushSMSResult]


class PushSMSDeliveryStatusWebhook(BaseModel):
    """
    Webhook payload containing SMS delivery status updates.

    Attributes:
        sn (str): Serial number of the gateway device.
        sms_deliver_status (List[PushSMSDeliveryStatus]): List of delivery statuses.
    """
    sn: str
    sms_deliver_status: List[PushSMSDeliveryStatus]


class PushUSSDWebhook(BaseModel):
    """
    Webhook payload containing USSD messages.

    Attributes:
        sn (str): Serial number of the gateway device.
        ussd (List[PushUSSD]): List of USSD messages.
    """
    sn: str
    ussd: List[PushUSSD]


class PushSIMRegisterWebhook(BaseModel):
    """
    Webhook payload containing SIM register statuses.

    Attributes:
        sn (str): Serial number of the gateway device.
        register (List[PushSIMRegister]): List of SIM register entries.
    """
    sn: str
    register: List[PushSIMRegister]


class PushCDRWebhook(BaseModel):
    """
    Webhook payload containing call detail records.

    Attributes:
        sn (str): Serial number of the gateway device.
        cdr (List[PushCDR]): List of call detail records.
    """
    sn: str
    cdr: List[PushCDR]


class PushDeviceWebhook(BaseModel):
    """
    Webhook payload containing device status info.

    Attributes:
        sn (str): Serial number of the gateway device.
        device (PushDevice): Device information.
    """
    sn: str
    device: PushDevice


class PushExceptionInfoWebhook(BaseModel):
    """
    Webhook payload containing exception info.

    Attributes:
        sn (str): Serial number of the gateway device.
        exception_info (PushExceptionInfo): Exception details.
    """
    sn: str
    exception_info: PushExceptionInfo

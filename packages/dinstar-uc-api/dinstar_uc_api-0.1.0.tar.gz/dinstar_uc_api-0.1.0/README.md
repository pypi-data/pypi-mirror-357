# dinstar-uc-api

A modern Python wrapper for the latest version of the Dinstar UC HTTP API.

This library provides typed access to Dinstar gateway endpoints for SMS, USSD, device status, port management, STK menus, and more. Built for developers who want clean, extendable, and well-documented access to gateway functionality.

---

## 📦 Features

- ✅ Send and receive SMS messages
- ✅ Manage USSD sessions and replies
- ✅ Monitor device and port status
- ✅ Query and interact with SIM Toolkit (STK) menus
- ✅ Typed dataclass models for responses
- ✅ Unified request logic via `send_api_request`

---

## 🚀 Installation

```bash
pip install dinstar-uc-api
```

## ⚙️ Configuration
Create a .env file in your root directory with the following:

```env
DINSTAR_USER=admin
DINSTAR_PASS=admin
DINSTAR_URL=https://your_gateway_ip
DINSTAR_VERIFY_SSL=false
```

This is accessed in code using decouple.config.

## 🧪 Quick Start with DinstarClient
```python
from dinstar.client import DinstarClient
from decouple import config

client = DinstarClient(
    username=config("DINSTAR_USER"),
    password=config("DINSTAR_PASS"),
    gateway_url=config("DINSTAR_URL"),
    verify_ssl=config("DINSTAR_VERIFY_SSL", cast=bool, default=True)
)

# Fetch unread SMS messages
sms = client.sms.receive_sms(flag="unread")
for msg in sms.data:
    print(f"[{msg.port}] {msg.number} → {msg.text}")

# Send USSD
ussd_response = client.ussd.send_ussd(text="*100#", ports=[0])
print(ussd_response)

# Query device performance
device_status = client.device.get_device_status()
print(device_status)
```

## 🧰 Example Scripts
Explore the examples/ folder:

- sms_fetch.py — Receive all SMS messages
- sms_send.py — Send a batch of SMS messages and track delivery
- send_ussd.py — Send and query USSD messages
- get_status.py — Query device performance (CPU, memory, flash)
- get_stk.py — Query STK menu and cancel
- set_port.py — Power ports on or off
- get_cdr.py — Query CDR logs

## 📚 Library Structure

| Module                   | Description                         |
| ------------------------ | ----------------------------------- |
| `dinstar.sms`            | SMS send, receive, queue, status    |
| `dinstar.ussd`           | USSD messaging and replies          |
| `dinstar.device`         | Device performance + SIM status     |
| `dinstar.port`           | Port info and control               |
| `dinstar.cdr`            | Call detail records                 |
| `dinstar.stk`            | STK menus and input                 |
| `dinstar.client`         | Unified wrapper across all modules  |
| `dinstar.models`         | Typed dataclasses for all responses |
| `dinstar.webhook_models` | Pydantic models for push events     |

## 🪪 License
This project is licensed under the terms of the MIT license.
For more details see [LICENSE](LICENSE)

## 🤝 Contributing
Pull requests welcome.
Please write clean code, include examples, and test API compatibility before submitting.

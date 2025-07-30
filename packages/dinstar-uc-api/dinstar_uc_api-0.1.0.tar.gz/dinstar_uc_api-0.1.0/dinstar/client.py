from .sms import DinstarSMS
from .port import DinstarPort
from .cdr import DinstarCDR
from .device import DinstarDevice
from .stk import DinstarSTK
from .ussd import DinstarUSSD

class DinstarClient:
    def __init__(self, username: str, password: str, gateway_url: str, verify_ssl: bool = True):
        self.username = username
        self.password = password
        self.gateway_url = gateway_url
        self.verify_ssl = verify_ssl

        init_kwargs = {
            "username": username,
            "password": password,
            "gateway_url": gateway_url,
            "verify_ssl": verify_ssl
        }

        self.sms = DinstarSMS(**init_kwargs)
        self.port = DinstarPort(**init_kwargs)
        self.cdr = DinstarCDR(**init_kwargs)
        self.device = DinstarDevice(**init_kwargs)
        self.stk = DinstarSTK(**init_kwargs)
        self.ussd = DinstarUSSD(**init_kwargs)

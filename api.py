import time
import hashlib
import logging
import requests  # Added missing import

_LOGGER = logging.getLogger(__name__)

class FoxESSApi:
    """FoxESS API interface using the official Open API domain."""

    # Updated to the official domain from the documentation
    BASE_URL = "https://www.foxesscloud.com" 

    def __init__(self, api_key, device_sn):
        self.api_key = api_key
        self.device_sn = device_sn

    def _headers(self, path, params=None):
        """
        This function is used to generate a signature consisting of URL, token, and timestamp, and return a dictionary containing the signature and other information.
            :param token: your key
            :param path:  your request path
            :param lang: language, default is English.
            :return: with authentication header
        """
        timestamp = round(time.time() * 1000)
        signature = rf"{path}\r\n{self.api_key}\r\n{timestamp}"
        # or use user_agent_rotator.get_random_user_agent() for user-agent
        return {
            "token": self.api_key,
            "lang": "en",
            "timestamp": str(timestamp),
            "Content-Type": "application/json",
            "signature": self.md5c(text=signature),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Safari/537.36",
            "Connection": "close",
        }
    
    @staticmethod
    def md5c(text="", _type="lower"):
        res = hashlib.md5(text.encode(encoding="UTF-8")).hexdigest()
        if _type.__eq__("lower"):
            return res
        else:
            return res.upper()

#    def _headers(self, path, params=None):

#        timestamp = round(time.time() * 1000)  # correct milliseconds string

#        # For GET requests with query params, include them in the signing string
#        if params:
#            query_str = "&".join(f"{k}={v}" for k, v in params.items())
#            sign_path = f"{path}?{query_str}"
#        else:
#            sign_path = path

#        sign_str = rf"{sign_path}\r\n{self.api_key}\r\n{timestamp}"
#        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()

#        return {
#            "token": self.api_key,
#            "timestamp": str(timestamp),
#            "signature": sign,
#            "Content-Type": "application/json",
#            "lang": "en",
#        }

    def get_charge_times(self):
        """Fetch and normalize data into a dictionary of integers."""
        path = "/op/v0/device/battery/forceChargeTime/get"
        params = {"sn": self.device_sn}
        headers = self._headers(path, params=params)
        
        r = requests.get(f"{self.BASE_URL}{path}", params=params, headers=headers, timeout=10)
        r.raise_for_status()
        response = r.json()

        if response.get("errno") != 0:
            raise Exception(f"FoxESS API error: {response}")

        res = response.get("result", {})
        if isinstance(res, list): res = res[0]

        # Store as integers for easy manipulation
        return {
            "h_start1": res.get("startTime1", {}).get("hour", 0),
            "m_start1": res.get("startTime1", {}).get("minute", 0),
            "h_end1": res.get("endTime1", {}).get("hour", 0),
            "m_end1": res.get("endTime1", {}).get("minute", 0),
            "h_start2": res.get("startTime2", {}).get("hour", 0),
            "m_start2": res.get("startTime2", {}).get("minute", 0),
            "h_end2": res.get("endTime2", {}).get("hour", 0),
            "m_end2": res.get("endTime2", {}).get("minute", 0),
            "enable1": bool(res.get("enable1", 0)),
            "enable2": bool(res.get("enable2", 0)),
        }

    def set_charge_times(self, h1_s, m1_s, h1_e, m1_e, h2_s, m2_s, h2_e, m2_e, en1, en2):
        """Push payload with separate hour/minute integers."""
        path = "/op/v0/device/battery/forceChargeTime/set"
        
        payload = {
            "sn": self.device_sn,
            "enable1": en1,
            "enable2": en2,
            "startTime1": {"hour": int(h1_s), "minute": int(m1_s)},
            "endTime1": {"hour": int(h1_e), "minute": int(m1_e)},
            "startTime2": {"hour": int(h2_s), "minute": int(m2_s)},
            "endTime2": {"hour": int(h2_e), "minute": int(m2_e)},
        }

        headers = self._headers(path)
        r = requests.post(f"{self.BASE_URL}{path}", json=payload, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()

    def set_enable(self, timer_key, enable):
        d = self.get_charge_times()
        if timer_key == "enable1":
            en1, en2 = enable, d["enable2"]
        else:
            en1, en2 = d["enable1"], enable
            
        return self.set_charge_times(
            d["h_start1"], d["m_start1"], d["h_end1"], d["m_end1"],
            d["h_start2"], d["m_start2"], d["h_end2"], d["m_end2"],
            en1, en2
        )

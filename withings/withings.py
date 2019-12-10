
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import requests
import time

LOGGER = polyinterface.LOGGER


def last_update():
    time_now = time.time()
    time_yesterday = time_now - 86400
    last_update_time = str(time_yesterday).split('.')[0]
    return last_update_time


def get_request(url, headers, payload):
    try:
        r = requests.post(url, headers=headers, data=payload)
        if r.status_code == requests.codes.ok:
            resp = r.json()
            print(resp)
            return resp
        else:
            LOGGER.error("Withings.get_request:  " + r.json())
            return None

    except requests.exceptions.RequestException as e:
        LOGGER.error("Error: " + str(e))


class Withings:
    def __init__(self, access_token):
        self.access_token = access_token

        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'Authorization': 'Bearer ' + self.access_token}

    def get_devices(self):
        url = "https://wbsapi.withings.net/v2/user"
        payload = {"action": "getdevice"}

        resp = get_request(url, self.headers, payload)
        if resp is not None:
            return resp
        else:
            LOGGER.error("Withings.get_devices is None")
            return None

    def get_measure(self):
        url = "https://wbsapi.withings.net/measure"
        payload = {"action": "getmeas", "lastupdate": last_update()}

        resp = get_request(url, self.headers, payload)
        if resp is not None:
            return resp
        else:
            LOGGER.error("Withings.get_measure is None")
            return None


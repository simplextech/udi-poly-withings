
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface

import requests

LOGGER = polyinterface.LOGGER


class Withings:
    def __init__(self, access_token):
        self.access_token = access_token
        self.api_url = "https://wbsapi.withings.net/v2/"

    def get_devices(self):
        _url = self.api_url + "user"

        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Authorization': 'Bearer ' + self.access_token
                   }

        payload = {"action": "getdevice"}

        try:
            r = requests.post(_url, headers=headers, data=payload)
            if r.status_code == requests.codes.ok:
                resp = r.json()
                print(resp)
                return resp
            else:
                LOGGER.error("Withings.get_devices:  " + r.json())
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))
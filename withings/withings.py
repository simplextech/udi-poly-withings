
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
    def __init__(self, access_token, ingress):
        self.access_token = access_token
        self.ingress = ingress

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
        payload = {"action": "getmeas", "lastupdate": last_update(), "offset": 1}

        resp = get_request(url, self.headers, payload)
        if resp is not None:
            return resp
        else:
            LOGGER.error("Withings.get_measure is None")
            return None

    def get_activities(self):
        url = "https://wbsapi.withings.net/v2/measure"
        payload = {"action": "getactivity", "lastupdate": last_update(), "offset": 1,
                   "data_fields": "steps,distance,elevation,soft,moderate,intense,active,calories,"
                                  "totalcalories,hr_average,hr_min,hr_max,hr_zone_0,hr_zone_1,hr_zone_2,hr_zone_3"}

        resp = get_request(url, self.headers, payload)
        if resp is not None:
            return resp
        else:
            LOGGER.error("Withings.get_measure is None")
            return None

    def get_sleep_summary(self):
        url = "https://wbsapi.withings.net/v2/sleep"
        payload = {"action": "getsummary", "lastupdate": last_update(),
                   "data_fields": "breathing_disturbances_intensity,deepsleepduration,durationtosleep,"
                                  "durationtowakeup,hr_average,hr_max,hr_min,lightsleepduration,remsleepduration,"
                                  "rr_average,rr_max,rr_min,sleep_score,snoring,snoringepisodecount,"
                                  "wakeupcount,wakeupduration"}

        resp = get_request(url, self.headers, payload)
        if resp is not None:
            return resp
        else:
            LOGGER.error("Withings.get_sleep_summary is None")

    def subscribe_bed_in(self):
        url = "https://wbsapi.withings.net/notify"
        # callbackurl = self.poly.init['netInfo']['httpsIngress']
        callbackurl = self.ingress
        payload = {"action": "subscribe", "appli": "50", "callbackurl": callbackurl}

        resp = get_request(url, self.headers, payload)
        if resp is not None:
            return True
        else:
            LOGGER.error("Withings.subscribe_bed_in Error: " + str(resp))
            return False

    def subscribe_bed_out(self):
        url = "https://wbsapi.withings.net/notify"
        # callbackurl = self.poly.init['netInfo']['httpsIngress']
        callbackurl = self.ingress
        payload = {"action": "subscribe", "appli": "51", "callbackurl": callbackurl}

        resp = get_request(url, self.headers, payload)
        if resp is not None:
            return True
        else:
            LOGGER.error("Withings.subscribe_bed_out Error: " + str(resp))
            return False

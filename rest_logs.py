import requests
import urllib.parse
import os
from dotenv import load_dotenv
load_dotenv()

def assertJsonSuccess(data):
    if 'status' in data and data['status'] == "error":
        print("Error: JSON object returns an error. " + str(data))
        return False
    else:
        return True

def get_token():
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = os.getenv("rest_url_base") + "/arcgis/admin/generateToken"
    
    params = urllib.parse.urlencode({'client': 'requestip', 'f': 'json'})
    body = {
        'username': os.getenv("rest_user"),
        'password': os.getenv("rest_pwd")
    }
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    response = requests.post(tokenURL, params=params, data=body, headers=headers, verify=False)

    if (response.status_code != 200):
        print("Error while fetching tokens from admin URL. Please check the URL and try again.")
        return
    else:
        data = response.json()

        if not assertJsonSuccess(data):            
            return
             
        return data["token"]   

def get_logs(token, level="SEVERE", server=None, services=None, startTime=None, endTime=None, pageSize=200000):
    url = os.getenv("rest_url_base") + "/arcgis/admin/logs/query"    
    if server is None:
        server = []
    server = [server] if not isinstance(server, list) else server
    if services is None:
        services = []
    services = [services] if not isinstance(services, list) else services
    params = {
        #'startTime': startTime,
        #'endTime': endTime,
        'level': level,
        'filter': {
            "codes": [],
            "processIds": [],
            "requestIds": [],
            "server": server,
            "services": services,
            "machines": ""
        },
        'filterType': 'json',
        'f': 'pjson',
        'pageSize': pageSize
    }
    if startTime is not None:
        params["startTime"] = startTime
    if endTime is not None:
        params["endTime"] = endTime
    
    params = urllib.parse.urlencode(params)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json", 'Authorization': f"Bearer {token}"}
    response = requests.post(url, params=params, headers=headers, verify=False)

    if not assertJsonSuccess(response.json()):            
            return
    return response.json()
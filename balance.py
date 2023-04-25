import requests
import csv
import time
import json
import ctypes
import threading
import tls_client
from utils import log,log_error,log_error_p,log_info,log_success

cookies=[]
proxies = []


with open('accounts.csv','r') as file:
    acc = csv.reader(file)
    header = next(acc)
    if header != None:
        for lines in acc:
            if lines[0]!='' and lines[1]!='':
                cookies.append(lines[0])
                proxies.append(lines[1])

with open("settings.json",'r',encoding='UTF-8') as file:
        FileData = json.load(file)
        CaptchaKey = FileData['UserData']['2capKey']
        UserAgent = FileData['UserData']['UserAgent']
        WebhookUrl = FileData['UserData']['WebhookUrl']
        MinimumDelay = FileData['UserData']['MinimumDelay']
        MaximumDelay = FileData['UserData']['MaximumDelay']

success = 0
errors = 0
def updatebar(Xsuccess,Xerrors):
    global success
    global errors

    success += Xsuccess
    errors += Xerrors
def time_elapsed():
    start_time = time.time() 
    while True:
        elapsed_time = time.time() - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed_time_str = "{:0>2}:{:0>2}:{:0>2}".format(int(hours), int(minutes), int(seconds))
        ctypes.windll.kernel32.SetConsoleTitleW(f"KeyDrop Balance by Rafał#6750 | Accounts: {len(cookies)} | Success: {success} Errors: {errors} | Time Elapsed: {elapsed_time_str}")
        time.sleep(1)

def SwitchString(proxy):
    if proxy == "x":
        proxy = ""
        return proxy
    else:
        proxy_ditails = proxy.split(":")
        pelneproxy = proxy_ditails[2]+":"+proxy_ditails[3]+"@"+proxy_ditails[0]+":"+proxy_ditails[1]
        proxies = {
                'http': 'http://'+pelneproxy,
                'https': 'http://'+pelneproxy}
        return proxies


def balance():
    threading.Thread(target=time_elapsed).start()
    total_value = 0
    for task in range(len(cookies)):
        session = tls_client.Session(     client_identifier="chrome_112" )
        cookie = cookies[task]
        headers = {
            'authority': 'key-drop.com',
            'User-Agent': UserAgent,
            'Cookie': cookie,
        }

        balance_req = session.get('https://key-drop.com/pl/panel/profil/eq_value', headers=headers,proxy=SwitchString(proxies[task]))
        if balance_req.status_code == 200:
            account_eq_value = balance_req.json()['fullPrice']
            log_success(f"[{task}] Eq Value: {account_eq_value}")
            updatebar(1,0)
            total_value+=float(account_eq_value)
        else:
            updatebar(0,1)
            log_error_p(balance_req.status_code)
    log_success(f"Accounts: {len(cookies)} | Total eq value: {round(total_value,2)} PLN")






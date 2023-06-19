import requests
import csv
import json
import ctypes
import time
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
            cookies.append(lines[0])
            proxies.append(lines[1])

with open("settings.json",'r',encoding='UTF-8') as file:
        FileData = json.load(file)
        CaptchaKey = FileData['UserData']['2capKey']
        UserAgent = FileData['UserData']['UserAgent']
        WebhookUrl = FileData['UserData']['WebhookUrl']
        MinimumDelay = FileData['UserData']['MinimumDelay']
        MaximumDelay = FileData['UserData']['MaximumDelay']
caseopened = 0
vouchers = 0
golds = 0
skins = 0

def updatebar(Xcaseopened,Xvouchers,Xgolds,Xskins):
    global caseopened
    global vouchers
    global golds
    global skins

    caseopened += Xcaseopened
    vouchers += Xvouchers
    golds += Xgolds
    skins += Xskins
    

def time_elapsed():
    start_time = time.time() 
    while True:
        elapsed_time = time.time() - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed_time_str = "{:0>2}:{:0>2}:{:0>2}".format(int(hours), int(minutes), int(seconds))
        ctypes.windll.kernel32.SetConsoleTitleW(f"KeyDrop DailyCase by Rafał#6750 | Accounts: {len(cookies)} | Case opened: {caseopened} Vouchers: {vouchers} Golds: {golds} Skins: {skins} | Time Elapsed: {elapsed_time_str}")
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

def DailyCase():
    threading.Thread(target=time_elapsed).start()
    for task in range(len(cookies)):
        session = tls_client.Session(     client_identifier="chrome_112" )
        cookie = cookies[task]
        headers = {
            'authority': 'key-drop.com',
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryqDIEeLh8ahuAyQ9P',
            'cookie': cookie,
            'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://key-drop.com/pl/daily-case',
            'user-agent': UserAgent,
        }

        data = '------WebKitFormBoundaryqDIEeLh8ahuAyQ9P\r\nContent-Disposition: form-data; name="level"\r\n\r\n0\r\n------WebKitFormBoundaryqDIEeLh8ahuAyQ9P--\r\n'

        daily_case_req = session.post('https://key-drop.com/pl/apiData/DailyFree/open', headers=headers,proxy=SwitchString(proxies[task]), data=data)

        if daily_case_req.status_code==200:
            try:
                if daily_case_req.json()['status']==True:
                    log_info(f"[{task}] Case opened!")
                    updatebar(1,0,0,0)
                    item_type = daily_case_req.json()['winnerData']['type']
                    if item_type == 'item':
                        updatebar(0,1,0,0)
                        title = daily_case_req.json()['winnerData']['prizeValue']['title']
                        value = daily_case_req.json()['winnerData']['prizeValue']['price']
                        log_success(f"[{task}] You received {title} {value} PLN")
                    if item_type == 'gold':
                        updatebar(0,0,1,0)
                        prize_value = daily_case_req.json()['winnerData']['prizeValue']
                        log_success(f"[{task}] You received {prize_value} GOLD")

                        
                if daily_case_req.json()['status']==False:
                    if daily_case_req.json()['error']=='W tej chwili nie możesz otworzyć tej skrzynki':
                        log(f"[{task}] You have already opened this case today! Try tomorrow :)")
                    if daily_case_req.json()['error']=="Twój avatar jest niepoprawny":
                        log_error_p(f"[{task}] Set keydrop_image as your steam avatar!")
            except Exception as er:
                if "Proxy responded with non 200 code: 407" in str(er):
                    log_error_p(f"[{task}] Connection error")
                    time.sleep(5)
                else:
                    log_error_p(str(er))
        else:
            print(daily_case_req.text)


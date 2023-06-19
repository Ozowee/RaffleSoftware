import requests
import json,csv
import time
import tls_client
import random
import ctypes
from discord_webhook import *
from utils import log,log_error,log_error_p,log_info,log_success,get_proxy


cookies=[]
proxies = []
threads = []



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

joins = 0
wins = 0
nonwins = 0
wins_value = 0

def updatebar(Xjoins,Xwins,Xnonwins,Xwins_value):
    global joins
    global wins
    global nonwins
    global wins_value

    joins += Xjoins
    wins += Xwins
    nonwins += Xnonwins
    wins_value += Xwins_value

def time_elapsed2():
    start_time = time.time() 
    while True:
        elapsed_time = time.time() - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed_time_str = "{:0>2}:{:0>2}:{:0>2}".format(int(hours), int(minutes), int(seconds))
        ctypes.windll.kernel32.SetConsoleTitleW(f"RafalAIO | Accounts: {len(cookies)} | Entries: {joins} Wins: {wins} NonWins: {nonwins} WinsValue: {wins_value} PLN | Time Elapsed: {elapsed_time_str}")
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

def Token(cookie,proxy):
    session = tls_client.Session(client_identifier="chrome_112" )
    headers = {
        'Host': 'key-drop.com',
        'user-agent': UserAgent,
        'Referer': 'https://key-drop.com/pl/',
        'Cookie': cookie,
    }

    params = {
        't': f'{int(time.time())}'
    }

    response = session.get('https://key-drop.com/pl/token', headers=headers,params=params,proxy=SwitchString(proxy))
    
    if response.status_code !=200:
        log_error_p(f"Token error [{response.status_code}] Sleeping 5s and getting new token...")
        time.sleep(5)
        response2 = session.get('https://key-drop.com/pl/token', headers=headers,params=params,proxy=SwitchString(proxy))

        bearer_token2 = response2.text
        return bearer_token2
    else:
        bearer_token = response.text

        return bearer_token

def CheckWinner(username,steamid,proxy,caseID,task_id):
    session = tls_client.Session(client_identifier="chrome_112" )
    headers_winner = {
    'Host': 'kdrp2.com',
    'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="113"',
    'x-currency': 'pln',
    'User-Agent': UserAgent,
    'sec-ch-ua-platform': '"Windows"',
    'Accept': '*/*',
    'Origin': 'https://key-drop.com',
    'Referer': 'https://key-drop.com/',
    'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
}
    while True:
        response_winner = session.get(f'https://kdrp2.com/CaseBattle/gameFullData/{caseID}', headers=headers_winner,proxy=SwitchString(proxy))
        if response_winner.status_code==200:
            if response_winner.json()['success']==True:
                if response_winner.json()['data']['status']=='ended':
                    if response_winner.json()['data']['wonSteamId']==steamid:
                        log_success(f"[{task_id}][{username}] You won a case battle!")
                        total_value = 0
                        for rounds in response_winner.json()['data']['rounds']:
                            for win_round in rounds['wonItems']:
                                val = win_round['price']*5
                                val = round(val,2)
                                total_value+=val
                        total_value = round(total_value,2)
                        updatebar(0,1,0,float(total_value))
                        break
                    else:
                        log_info(f"[{task_id}][{username}] You are not a winner!")
                        updatebar(0,0,1,0)
                        break
                else:
                    log_info(f"[{task_id}][{username}] waiting for results")
                    time.sleep(5)
                    continue
            if response_winner.json()['success']==False:
                print(response_winner.text)
                break
        else:
            print("Conn error")
            break

def CaseBattle(cookie,proxy,task_id):
    try:
        task_id = '{:03}'.format(task_id+1)
        session = tls_client.Session(client_identifier="chrome_112" )
        headers = {
            'Host': 'kdrp2.com',
            'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="112"',
            'x-currency': 'pln',
            'User-Agent': UserAgent,
            'sec-ch-ua-platform': '"Windows"',
            'Accept': '*/*',
            'Origin': 'https://key-drop.com',
            'Referer': 'https://key-drop.com/',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        params = {
            'type': 'active',
            'page': '0',
            'priceFrom': '0',
            'priceTo': 'undefined',
            'searchText': '',
            'sort': 'latest',
            'players': 'all',
            'roundsCount': 'all',
        }

        free_giveaway = 'x'
        scrap_r = session.get('https://kdrp2.com/CaseBattle/battle', params=params, headers=headers,proxy=get_proxy())
        if scrap_r.status_code == 200:
            for i in scrap_r.json()['data']:
                if i['isFreeBattle'] == True and i['freeBattleTicketCost']==1:
                    free_giveaway = i['id']
        else:
            log_error_p(f"[{task_id}] conn error")
        while True:
            new_free_giveaway = 'x'
            max_users = 0
            scrap_r2 = session.get('https://kdrp2.com/CaseBattle/battle', params=params, headers=headers,proxy=get_proxy())
            if scrap_r2.status_code == 200:
                for i in scrap_r2.json()['data']:
                    if i['isFreeBattle'] == True and i['freeBattleTicketCost']==1:
                        new_free_giveaway = i['id']
                        max_users = i['maxUserCount']
            else:
                log_error_p(f"[{task_id}] conn error")

            
            if new_free_giveaway!=free_giveaway:
                headers_join = {
                'Host': 'kdrp2.com',
                'sec-ch-ua': '"Not?A_Brand";v="99", "Opera GX";v="97", "Chromium";v="111"',
                'x-currency': 'pln',
                'sec-ch-ua-mobile': '?0',
                'Authorization': f'Bearer {Token(cookie,proxy)}',
                'User-Agent': UserAgent,
                'sec-ch-ua-platform': '"Windows"',
                'Accept': '*/*',
                'Origin': 'https://key-drop.com',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://key-drop.com/',
                'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
                try:
                    random_slot = random.randint(0,max_users-1)
                    join_casebattle = session.post(f'https://kdrp2.com/CaseBattle/joinCaseBattle/{new_free_giveaway}/0', headers=headers_join,proxy=SwitchString(proxy))
                    if join_casebattle.json()['success']==True:
                        updatebar(1,0,0,0)
                        username = join_casebattle.json()['data']['username']
                        steamid = join_casebattle.json()['data']['idSteam']
                        slot = join_casebattle.json()['data']['slot']
                        log_success(f"[{task_id}][{username}] successfully joined free case battle | BattleID: {new_free_giveaway} | slot: {slot}")
                        CheckWinner(username,steamid,proxy,new_free_giveaway,task_id)
                        break
                    if join_casebattle.json()['success']==False:
                        if join_casebattle.json()['errorCode']=='slotUnavailable':
                            log_error_p(f"[{task_id}] slot unavailable")
                            time.sleep(2)
                            continue
                        if join_casebattle.json()['errorCode']=='userHasToWaitBeforeJoiningFreeBattle':
                            time_to_wait = str(join_casebattle.json()['message']).split(" before")[0].split("wait ")[1]
                            log_info(f"[{task_id}] You have to wait {time_to_wait} before join the next free battle")
                            break
                        if join_casebattle.json()['errorCode']=='notEnoughtMoney':
                            log_error_p(f"[{task_id}] You don't have enought tickets")
                            break
                        else:
                            print(join_casebattle.text)
                            break
                    if join_casebattle.json()['statusCode']==404:
                        log_error_p(f"[{task_id}] 404")
                        break
                except Exception as er:
                    log_info(f"[{task_id}] {str(er)}")
                    continue
            else:
                log(f"[{task_id}] looking for free case battle")
                continue
    except Exception as er:
        if "Proxy responded with non 200 code: 407" in str(er):
                log_error_p(f"[{task_id}] Connection error, waiting 5s")
                time.sleep(5)
        if "empty range for randrange()" in str(er):
            log_error_p(f"[{task_id}] Error on joining")
            free_giveaway = new_free_giveaway
        else:
            log_error_p(str(er))


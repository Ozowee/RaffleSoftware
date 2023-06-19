import requests
import time
import tls_client
import csv
import random
import json
import ctypes
import threading
import traceback,sys
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
        CaptchaAPIkey = FileData['UserData']['2capKey']
        UserAgent = FileData['UserData']['UserAgent']
        WebhookUrl = FileData['UserData']['WebhookUrl']
        MinimumDelay = FileData['UserData']['MinimumDelay']
        MaximumDelay = FileData['UserData']['MaximumDelay']
        MinimumGiveawayValueToJoin = FileData['UserData']['MinimumGiveawayValueToJoin']

joins = 0
wins = 0
captcha_bar = 0
nonwins = 0
acc_hold = 0
acc_failed = 0
acc_not_eligible = 0
global_username = ""

def updatebar(Xjoins,Xwins,Xcaptcha,Xacchold,Xaccfailed,XaccNotEligible):
    global joins
    global wins
    global captcha_bar
    global acc_hold
    global acc_failed
    global acc_not_eligible 

    joins += Xjoins
    wins += Xwins
    captcha_bar += Xcaptcha
    acc_hold += Xacchold
    acc_failed += Xaccfailed
    acc_not_eligible += XaccNotEligible

def time_elapsed():
    start_time = time.time() 
    while True:
        elapsed_time = time.time() - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed_time_str = "{:0>2}:{:0>2}:{:0>2}".format(int(hours), int(minutes), int(seconds))
        ctypes.windll.kernel32.SetConsoleTitleW(f"RafalAIO | Accounts: {len(cookies)} | Entries: {joins} Wins: {wins} Captchas: {captcha_bar} HoldAccounts: {acc_hold} FailedAccounts: {acc_failed} NotEligible: {acc_not_eligible} | Time Elapsed: {elapsed_time_str}")
        time.sleep(1)

def SaveUsername(user):
    global global_username
    global_username = user
    

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
    session = tls_client.Session(     client_identifier="chrome_112" )
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
    
def CheckWinner(giveaway_id,username,cookie,task_id,proxy):
    session = tls_client.Session(     client_identifier="chrome_112" )
    headers_winner = {
    'Accept': '*/*',
    'Authorization': f'Bearer {Token(cookie,proxy)}',
    'Origin': 'https://key-drop.com',
    'Referer': 'https://key-drop.com/',
    'user-agent': UserAgent,
    'x-currency': 'PLN',
    }
    winners = []
    total_price_value = 0
    response_winner = session.get(f'https://wss-2061.key-drop.com/v1/giveaway//data/{giveaway_id}', headers=headers_winner,proxy=SwitchString(proxy))
    MySteamID = response_winner.json()['data']['mySteamId']
    
    for w in response_winner.json()['data']['winners']:
        winners.append(w['userdata']['idSteam'])
    if MySteamID in winners:
        log_success(f"[{task_id}][{giveaway_id}][{username}] You won a giveaway")
        updatebar(0,1,0,0,0,0)
        for element in response_winner.json()['data']['winners']:
            if MySteamID==element['userdata']['idSteam']:
                prizeID =element['prizeId'] 
                for prize in response_winner.json()['data']['prizes']:
                    if prizeID==prize['id']:
                        log_success(f"[{task_id}][{giveaway_id}][{username}] Found your prize!")
                        skin = f"{prize['title']} {prize['subtitle']}"
                        price = f"{prize['price']} PLN"
                        photo = f"https://cdn.key-drop.com/{prize['itemImg']}"
                        webhook = DiscordWebhook(url=WebhookUrl, username = f'Keydrop Giveaways',avatar_url='https://i.imgur.com/bH3m3DT.jpeg',timeout=10)
                        embed = DiscordEmbed(title="Keydrop Giveaway",url=f"https://key-drop.com/pl/giveaways/keydrop/{giveaway_id}", color='0x50d68d',description=f"[{username}] You Won a giveaway!")
                        embed.set_thumbnail(url = photo)
                        embed.add_embed_field(name='Item:', value=skin,inline=True)
                        embed.add_embed_field(name='Value:', value=price,inline=True)
                        embed.set_footer(text=f'RafalAIO by Rafal#6750',icon_url = 'https://i.imgur.com/bH3m3DT.jpeg')
                        webhook.add_embed(embed)
                        webhook.execute()
    else:
        log(f"[{task_id}][{giveaway_id}][{username}] You're not a Winner")

def Monitor(cookie,task_id,proxy,gw_type): 
    try:
        session = tls_client.Session(     client_identifier="chrome_112" )
        updatebar(0,0,0,0,0,0)
        task_id = '{:03}'.format(task_id+1)

        headers_giveaway_list = {
        'Accept': '*/*',
        'Origin': 'https://key-drop.com',
        'Referer': 'https://key-drop.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'x-currency': 'PLN',
        }

        params_giveaway_list = {
            'type': 'active',
            'page': '0',
            'perPage': '5',
            'status': 'active',
            'sort': 'latest',
        }

        id_giveaway = ''
        id_new_giveaway = ''
        giveway_list = session.get('https://wss-2061.key-drop.com/v1/giveaway//list', params=params_giveaway_list, headers=headers_giveaway_list,proxy=get_proxy())
        if giveway_list.status_code==200:
            for id in giveway_list.json()['data']:
                if id['frequency']==gw_type and id['status']=='new' and id['prizes'][0]['price']>=MinimumGiveawayValueToJoin:
                        id_giveaway = id['id']
        if giveway_list.status_code==403:
            log_error_p(f"[{task_id}][{giveway_list.status_code}] Failed to scrap giveaway id! Changing monitor proxy")
    except Exception as tls_er:
            if "i/o timeout" in str(tls_er):
                    log_error_p(f"[{task_id}][{giveway_list.status_code}] Timeout on monitoring, waiting 5s")
                    time.sleep(5)  
            else:
                log_error_p(f"{tls_er}")
                time.sleep(5) 

    while True:
        try:
            giveway_list_new = session.get('https://wss-2061.key-drop.com/v1/giveaway//list', params=params_giveaway_list, headers=headers_giveaway_list,proxy=get_proxy())
            if giveway_list_new.status_code ==200:
                try:
                    for id in giveway_list_new.json()['data']:
                        if id['frequency']==gw_type and id['status']=='new' and id['prizes'][0]['price']>=MinimumGiveawayValueToJoin:
                                id_new_giveaway = id['id']
                except KeyError:
                    print(giveway_list_new.text)
                    
            if giveway_list.status_code==403:
                log_error_p(f"[{task_id}][{giveway_list.status_code}] Failed to scrap giveaway id! Changing monitor proxy")
                continue
                
                
        except Exception as tls_er:
            if "i/o timeout" in str(tls_er):
                    log_error_p(f"[{task_id}][{giveway_list_new.status_code}] Timeout on monitoring, waiting 5s")
                    time.sleep(5)
                    continue
                      
            else:
                log_error_p(f"[{task_id}][{giveway_list_new.status_code}] {tls_er}")
                time.sleep(5)
                
        
        if id_new_giveaway != id_giveaway:
            try:
                headers_join = {
                    'authority': 'wss-2061.key-drop.com',
                    'accept': '*/*',
                    'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Authorization': f'Bearer {Token(cookie,proxy)}',
                    'content-type': 'application/json',
                    'dnt': '1',
                    'origin': 'https://key-drop.com',
                    'referer': 'https://key-drop.com/',
                    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                    'x-requested-with': 'XMLHttpRequest',
                    'user-agent': UserAgent,
                }
                response_join = session.put(f'https://wss-3002.key-drop.com/v1/giveaway//joinGiveaway/{id_new_giveaway}', headers=headers_join,proxy=SwitchString(proxy))
                if response_join.status_code == 200:
                    if response_join.json()['success']==True:
                        updatebar(1,0,0,0,0,0)
                        username = response_join.json()['data']['username']
                        SaveUsername(username)
                        slot = response_join.json()['data']['slot']
                        log_success(f"[{task_id}][{id_new_giveaway}][{username}] Successfully joined giveaway! Slot {slot}/1000")
                        if len(id_giveaway) > 1:
                            CheckWinner(id_giveaway,username,cookie,task_id,proxy)
                        id_giveaway = id_new_giveaway
                        
                        continue
                    

                    if response_join.json()['success']==False:
                        if response_join.json()['errorCode']=='userHasToWaitBeforeJoiningGiveaway':
                            if "Congratulations" in response_join.json()['message']:
                                strip_str = str(response_join.json()['message']).split("You can join again in our giveaway in just ")[1]

                                hours, minutes, seconds = [int(time[:-1]) for time in strip_str.split()]
                                total_seconds = (hours * 3600) + (minutes * 60) + seconds
                                
                                if len(id_giveaway) > 1:
                                    CheckWinner(id_giveaway,global_username,cookie,task_id,proxy)    
                                log_info(f"[{task_id}][{id_new_giveaway}] You have to wait before entering new raffle! Waiting {strip_str}")
                                updatebar(0,0,0,1,0,0)
                                time.sleep(total_seconds)
                                updatebar(0,0,0,-1,0,0)
                                log_success(f"[{task_id}][{id_new_giveaway}] Back to monitoring after a {strip_str} timeout!")
                                id_giveaway = id_new_giveaway
                                continue
                            if "You must wait" in response_join.json()['message']:
                                strip_str = str(response_join.json()['message']).split("You must wait ")[1].split(" before joining the next giveaway.")[0]

                                hours, minutes, seconds = [int(time[:-1]) for time in strip_str.split()]
                                total_seconds = (hours * 3600) + (minutes * 60) + seconds
                                if len(id_giveaway) > 1:
                                    CheckWinner(id_giveaway,global_username,cookie,task_id,proxy)
                                log_info(f"[{task_id}][{id_new_giveaway}] You have to wait before entering new raffle! Waiting {strip_str}")
                                updatebar(0,0,0,1,0,0)
                                time.sleep(total_seconds)
                                updatebar(0,0,0,-1,0,0)
                                log_success(f"[{task_id}][{id_new_giveaway}] Back to monitoring after a {strip_str} timeout!")
                                id_giveaway = id_new_giveaway
                                continue
                        else:
                            if response_join.json()['message']=='captcha':
                                log_info(f"[{task_id}] Captcha detected!")
                                captchaKey = '6Ld2uggaAAAAAG9YRZYZkIhCdS38FZYpY9RRYkwN'
                                website_url = 'https://key-drop.com/en/giveaways/keydrop'
                                api_key = CaptchaAPIkey
                                success = False
                                for i in range(3):
                                    if success == False:
                                        responsea = requests.get(f'https://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={captchaKey}&pageurl={website_url}')
                                        while True:
                                            response = requests.get(f'https://2captcha.com/res.php?key={api_key}&action=get&id={responsea.text.split("|")[1]}')
                                            time.sleep(1)
                                            if str(response.text) == 'ERROR_CAPTCHA_UNSOLVABLE':
                                                log_error('Captcha unsolvable')
                                                break
                                            if len(response.text) > 50:
                                                success = True
                                                captcha = response.text.split("|")[1]
                                                
                                                break
                                            else:
                                                continue
                                json_data = {
                                'captcha': captcha,
                                }
                                log(f"[{task_id}][{id_new_giveaway}] Captcha sent!")
                                time.sleep(1)

                                response_join2 = session.put(f'https://wss-3002.key-drop.com/v1/giveaway//joinGiveaway/{id_new_giveaway}', headers=headers_join, json=json_data)
                                if response_join2.status_code==200:
                                    data = response_join2.json()
                                    if data['success'] == True:
                                        updatebar(1,0,0,0,0,0)
                                        updatebar(0,0,1,0,0,0)
                                        log_success(f"[{task_id}] Captcha solved!")
                                        username = response_join2.json()['data']['username']
                                        slot = response_join2.json()['data']['slot']
                                        SaveUsername(username)
                                        log_success(f"[{task_id}][{id_new_giveaway}][{username}] Successfully joined giveaway! {slot}/1000")
                                        if len(id_giveaway) > 1:
                                            CheckWinner(id_giveaway,username,cookie,task_id,proxy)
                                        id_giveaway = id_new_giveaway
                                        
                                        continue
                                    if data['success'] == False:
                                        if data['errorCode']=='userHasToWaitBeforeJoiningGiveaway':
                                            if "Congratulations" in data['message']:
                                                strip_str = str(data['message']).split("You can join again in our giveaway in just ")[1]

                                                hours, minutes, seconds = [int(time[:-1]) for time in strip_str.split()]
                                                total_seconds = (hours * 3600) + (minutes * 60) + seconds
                                                if len(id_giveaway) > 1:
                                                    CheckWinner(id_giveaway,global_username,cookie,task_id,proxy)
                                                log_info(f"[{task_id}][{id_new_giveaway}] You have to wait before entering new raffle! Waiting {strip_str}")
                                                updatebar(0,0,0,1,0,0)
                                                time.sleep(total_seconds)
                                                updatebar(0,0,0,-1,0,0)
                                                log_success(f"[{task_id}][{id_new_giveaway}] Back to monitoring after a {strip_str} timeout!")
                                                id_giveaway = id_new_giveaway
                                                continue
                                            if "You must wait" in data['message']:
                                                strip_str = str(data['message']).split("You must wait ")[1].split(" before joining the next giveaway.")[0]

                                                hours, minutes, seconds = [int(time[:-1]) for time in strip_str.split()]
                                                total_seconds = (hours * 3600) + (minutes * 60) + seconds
                                                if len(id_giveaway) > 1:
                                                    CheckWinner(id_giveaway,global_username,cookie,task_id,proxy)
                                                log_info(f"[{task_id}][{id_new_giveaway}] You have to wait before entering new raffle! Waiting {strip_str}")
                                                updatebar(0,0,0,1,0,0)
                                                time.sleep(total_seconds)
                                                updatebar(0,0,0,-1,0,0)
                                                log_success(f"[{task_id}][{id_new_giveaway}] Back to monitoring after a 6h timeout!")
                                                id_giveaway = id_new_giveaway
                                                continue
                                        else:
                                            if data['message']== 'Giveaway expired...':
                                                log_error_p(f"[{task_id}][{id_new_giveaway}] Giveaway expired!")
                                                updatebar(0,0,1,0,0,0)
                                                id_giveaway = id_new_giveaway
                                                continue
                                            if "You must wait" in str(data['message']):
                                                log_error_p(f"[{task_id}][{id_new_giveaway}] You won a giveaway recently! Waiting 1h")
                                                time.sleep(3600)
                                                id_giveaway = id_new_giveaway
                                                continue
                                            if data['message']=='please wait 10 secounds..':
                                                log_error_p(f"[{task_id}][{id_new_giveaway}] Rate Limited! Waiting 10s")
                                                id_giveaway = id_new_giveaway
                                                time.sleep(10)
                                                continue
                                            if data['message']=='already join..':
                                                updatebar(1,0,0,0,0,0)
                                                log_success(f"[{task_id}][{id_new_giveaway}] Successfully joined giveaway!")
                                                id_giveaway = id_new_giveaway
                                                continue
                                            if data['errorCode']=='giveawayLimitPlayers':
                                                updatebar(0,0,1,0,0,0)
                                                log_error_p(f"[{task_id}][{id_new_giveaway}] Giveaway is full!")
                                                id_giveaway = id_new_giveaway
                                                continue
                                            if data['errorCode']=='requirementDepositAmount':
                                                log_error_p(f"[{task_id}][{id_new_giveaway}] you're not eligible to this giveaway! Stopping task")
                                                updatebar(0,0,0,0,0,1)
                                                break
                                            if data['message']=='unknown':
                                                log_error_p(f"[{task_id}][{id_new_giveaway}] Unknown error! Retrying in 5s")
                                                time.sleep(5)
                                                continue
                                            else:
                                                if data['message']=='captcha':
                                                    log_error_p(f"[{task_id}][{id_new_giveaway}] Captcha failed to post")
                                                    id_giveaway = id_new_giveaway
                                                    break
                                                else:
                                                    log_error_p(f"[{task_id}] {data}")
                                                    time.sleep(10)
                                                    id_giveaway = id_new_giveaway
                                                    continue
                                else:
                                    log_error_p(f"[{task_id}][{id_new_giveaway}][{response_join.status_code}] Keydrop servers are dead!")
                                    time.sleep(1)
                                    continue
                            if response_join.json()['message']=='Giveaway expired...':
                                log_error_p(f"[{task_id}][{id_new_giveaway}] Giveaway expired!")
                                id_giveaway = id_new_giveaway
                                continue
                            if response_join.json()['message']=='please wait 10 secounds..':
                                log_error_p(f"[{task_id}][{id_new_giveaway}] Rate Limited! Waiting 5s")
                                time.sleep(5)
                                continue
                            if response_join.json()['errorCode']=='giveawayLimitPlayers':
                                log_error_p(f"[{task_id}][{id_new_giveaway}] Giveaway is full!")
                                id_giveaway = id_new_giveaway
                                continue
                            if response_join.json()['message']=='already join..':
                                log(f"[{task_id}][{id_new_giveaway}] You already joined into this giveaway!")
                                updatebar(1,0,0,0,0,0)
                                id_giveaway = id_new_giveaway
                                continue
                            if response_join.json()['message']=='not logged in':
                                log_error_p(f"[{task_id}][{id_new_giveaway}][{response_join.status_code}] Account logged out! Login again and update the cookie")
                                updatebar(0,0,0,0,1,0)
                                break
                            if response_join.json()['errorCode']=='requirementDepositAmount':
                                log_error_p(f"[{task_id}][{id_new_giveaway}] you're not eligible to this giveaway! Stopping task")
                                updatebar(0,0,0,0,0,1)
                                break
                            if response_join.json()['message']=='unknown':
                                log_error_p(f"[{task_id}][{id_new_giveaway}] Unknown error! Retrying in 5s")
                                time.sleep(5)
                                continue
                            else:
                                log_error_p(f"[{task_id}] {response_join.text}")
                                id_giveaway = id_new_giveaway
                                continue
                                       
                else:
                    if response_join.status_code==403:
                        log_error_p(f"[{task_id}][{id_new_giveaway}][{response_join.status_code}] Check your Account/Change Account Proxy!")
                        updatebar(0,0,0,0,1,0)
                        break
                    else:
                        log_error_p(f"[{task_id}][{id_new_giveaway}][{response_join.status_code}] Keydrop servers are dead!")
                        time.sleep(2)
                        continue

                    
            except requests.exceptions.ConnectionError as req_proxy:
                log_error_p(f"[{task_id}][{id_giveaway}] Connection error, waiting 5s")
                time.sleep(5)
                continue

            except Exception as er:
                if "i/o timeout" in str(er):
                    log_error_p(f"[{task_id}] Timeout on joining, retrying in 5s")
                    time.sleep(5)
                    continue  
                if "(Client.Timeout exceeded while awaiting headers)" in str(er):
                    log_error_p(f"[{task_id}] Timeout on joining, retrying in 5s")
                    time.sleep(5)
                    continue 
                if "Proxy responded with non 200 code: 407" in str(er):
                    log_error_p(f"[{task_id}] Connection error, waiting 5s")
                    time.sleep(5)
                    continue
                else:
                    log_error_p(f"[{task_id}] {er}")
                    time.sleep(5)
                    continue
        else:
            time_sleep = random.randint(MinimumDelay,MaximumDelay)
            log_info(f"[{task_id}][{id_giveaway}] Waiting for new giveaway...({time_sleep}s)")
            time.sleep(time_sleep)
            continue


# if __name__ == "__main__":
#     for task in range(len(cookies)):
#         gw_type = "amateur"
#         thread = threading.Thread(target=Monitor,args=(cookies[task],task,proxies[task],gw_type)).start()
#     threading.Thread(target=time_elapsed).start()
    

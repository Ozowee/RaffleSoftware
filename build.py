from utils import log,log_error,log_error_p,log_info,log_success,logo
from  main_tls import Monitor,time_elapsed
from balance import balance
from daily_case import DailyCase
import threading
import requests
import time
import csv,json


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
        licence_whop = FileData['UserData']['License']

with open("access.json",'r') as accessFile:
    jsonFile = json.load(accessFile)
    whopAuthPart1 = jsonFile['Keys']['whopAuthPart1']
    whopAuthPart2 = jsonFile['Keys']['whopAuthPart2']
    whopAuthPart3 = jsonFile['Keys']['whopAuthPart3']

def build():
    misio1 = whopAuthPart1
    misio2 = whopAuthPart2
    misio3 = whopAuthPart3
    
    whop_headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {misio3}"}

    whop_r = requests.get(f'https://api.whop.com/api/v2/memberships/{licence_whop}',headers=whop_headers) 
    whop_response = whop_r.json()
    log_info("Checking licence")
    if whop_r.status_code==200:
        if whop_response['valid'] == True:
            isKeyValid = True
            logo("""
                ██████╗  █████╗ ███████╗ █████╗ ██╗      █████╗ ██╗ ██████╗ 
                ██╔══██╗██╔══██╗██╔════╝██╔══██╗██║     ██╔══██╗██║██╔═══██╗
                ██████╔╝███████║█████╗  ███████║██║     ███████║██║██║   ██║
                ██╔══██╗██╔══██║██╔══╝  ██╔══██║██║     ██╔══██║██║██║   ██║
                ██║  ██║██║  ██║██║     ██║  ██║███████╗██║  ██║██║╚██████╔╝
                ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝                                                                                                  
            """)
            if len(cookies)>20 or len(cookies)==0:
                if len(cookies)>10:
                    log_error_p("Too many task! User limit: 10!")
                    time.sleep(1)
                    input("Press enter to exit")
                if len(cookies)<1:
                    log_error_p("Fill accounts.csv before starting!")
                    time.sleep(1)
                    input("Press enter to exit")
            else:
                log_info("1 | Giveaway Joiner")
                log_info("2 | Daily Case Opener")
                log_info("3 | Balance Checker")
                option = input("Option: ")

                if option == "1":
                    log_info("1 - amateur")
                    log_info("2 - contender")
                    gw_option = input("Option: ")
                    if gw_option == "1":
                        gw_type = "amateur"
                        for task in range(len(cookies)):
                            thread = threading.Thread(target=Monitor,args=(cookies[task],task,proxies[task],gw_type)).start()
                        threading.Thread(target=time_elapsed).start()
                    if gw_option == "2":
                        gw_type = "contender"
                        for task in range(len(cookies)):
                            thread = threading.Thread(target=Monitor,args=(cookies[task],task,proxies[task],gw_type)).start()
                        threading.Thread(target=time_elapsed).start()
                if option == "2":
                    DailyCase()
                if option == "3":
                    balance()
                    
    else:
        log_error_p("Wrong licence key!")
        time.sleep(1)
        input("Press enter to exit")
build()
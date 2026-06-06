#!/usr/bin/python3
#v-idk
try:
    import requests
except:
    os.system("pip3 install requests")
    import requests
import json
import os
import time
import random
from datetime import datetime, date, timedelta
#from multiprocessing import Process, Queue
import _thread
import sys
import socket

#-------------------------KEYS SECTION-------------------------------------------------------
username = "REPLACE_WITH_YOUR_TOKENS_ETC_FROM_PCO_DEV_PAGE"
password = "REPLACE_WITH_YOUR_TOKENS_ETC_FROM_PCO_DEV_PAGE"
#-------------------------KEYS SECTION-------------------------------------------------------

#-------------------------CONFIG SECTION---------------------------
campus_name = "PSL |"
service_type_list = []
preroll_offset = -127

propresenter_active = False
#enable ProPresenter send via HTTP API
propresenter_machine_ip = "127.0.0.1"
#IP for ProPresenter machine (should be 127.0.0.1 if on that machine)
propresenter_machine_port = "1025"
#port for ProPresenter machine
filter_for_today_only = False
#filter for plans only happening today
filter_forward_days = 6
#how many days to look forward for for plans
filter_backward_days = 1
#how many days ago to load plans from
threading_load_plans = True
#load service_types/plans in threaded mode

data_display = False
#display all data instead of just time and item name


configure_map = {
    "propresenter_active": "True/False (HTTP ProPresenter StageMessage API)",
    "propresenter_machine_ip": "ProPresenter machine IP or 127.0.0.1 if this computer",
    "propresenter_machine_port": "ProPresenter machine port (found in settings)",
    "campus_name": f"Campus name (eg. PSL) in format \"PSL |\"",
    "preroll_offset": "negative int of preroll length in seconds (eg. -127)",
    "filter_for_today_only": "True/False (capitalized first letter)",
    "filter_forward_days": "number of days to look at in advance for plans",
    "filter_backward_days": "if you need to load a multiday plan from yesterday etc.",
    "threading_load_plans": "enable multithreader for plans loading",
    "short_display": "short display mode for small terminals (True/False)"
 } #map for splicer configurator

persist_map = [
    "username",
    "password",
    "person_id"
] #map for additional settings used in crossover

#-------------------------CONFIG SECTION---------------------------

#source: idk google said this works and apparently it actually does
class color:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BK_RED = '\033[41m'
    BK_GREEN = '\033[42m'
    BK_YELLOW = '\033[43m'
    BK_BLUE = '\033[44m'
    BK_MAGENTA = '\033[45m'
    BK_CYAN = '\033[46m'
    BK_WHITE = '\033[47m'


service_list = [] #[[service type, plan number, dates+title]]

system_name = socket.gethostname()

def get_parameter(parameter):
    with open(__file__, 'r') as file:
        for line in file:
            if parameter in line:
                return ' '.join(line.split(' ')[2:]).replace('\n', '')
        return 99

def splicer(parameter, setting):
    file_as_list = []
    swapped = False
    with open(__file__, 'r') as file:
        for line in file:
            if parameter in line and not swapped:
                try:
                    file_as_list.append(f"{parameter} = {int(setting)}\n")
                except:
                    if setting == "True" or setting == "False":
                        file_as_list.append(f"{parameter} = {setting}")
                    else:
                        file_as_list.append(f"{parameter} = \"{setting}\"\n")
                swapped = True
            else:
                file_as_list.append(line)
    file.close()
    with open(__file__, 'w') as file:
        for line in file_as_list:
            file.write(line)

def restart():
    sys.stdout.flush() 
    sys.stderr.flush()
    os.execv(sys.executable, ['python3'] + sys.argv)

def update():
    print(f"{color.GREEN}--UPDATING--{color.RESET}")
    try:
        t = 0
        print(1/t)
    except:
        print(f"{color.BLUE}--UPDATING FROM GITHUB--{color.RESET}")
        os.system(f"curl -L -o {__file__} https://githubusercontent.com/K-256/planning_center_thingy/glassrock.py")
    for i in configure_map:
        print(f"REMAPPING {i}")
        splicer(i, globals()[i])
    for i in persist_map:
        print(f"REMAPPING {i}")
        splicer(i, globals()[i])
    print(f"{color.RED}--RESTARTING--{color.RESET}")
    time.sleep(1)
    restart()

def configure(configure_map):
    for parameter in configure_map:
        os.system("clear")
        print(color.YELLOW+color.BOLD+"------CONFIGURE------", color.RESET)
        print(color.YELLOW+"   (enter to skip)", color.RESET)
        print(color.MAGENTA+color.BOLD+parameter+" - "+color.RESET+configure_map[parameter], "\n")
        setting = input(f"{color.GREEN}{parameter}{color.RESET} ({get_parameter(parameter)}) >> ")
        if setting == '':
            print(color.YELLOW, "SKIPPING", color.RESET)
        else:
            print(color.BLUE, f"SETTING {parameter} to {setting}", color.RESET)
            splicer(parameter, setting)
        time.sleep(0.6)
    print(f"{color.GREEN}FINISHED CONFIGURATION, RESETTING{color.RESET}")
    time.sleep(1)
    restart()
    
def load_service_types():
    print(f"{color.BLUE}LOADING SERVICE TYPES{color.RESET}")
    global service_type_list
    service_type_list = []
    service_type_page = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types?where[name]={campus_name}&per_page=100", auth=(username, password))
    service_type_list = service_type_list + [[service_type['id'], -18000, service_type['attributes']['name']] for service_type in service_type_page.json()['data'] if campus_name in service_type['attributes']['name']]

plan_loading_count = 0
def load_plans_for_service_type(service_type):
    done = False
    global plan_loading_count
    global service_list
    plan_loading_count += 1
    while not done:
        try:
            print(f"LOADING SERVICE TYPE: {color.BLUE}{service_type[0]}{color.RESET}")
            total_service_count = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type[0]}/plans?offset=9999", auth=(username, password))
            total_service_count = int(total_service_count.json()['meta']['total_count'])
            print(f"SERVICE COUNT: {color.CYAN}{total_service_count}{color.RESET}")
            service_type_name = service_type[2]
            print(f"SERVICE TYPE NAME: {color.CYAN}{service_type_name}{color.RESET}")
            service_page = requests.get(f"http://api.planningcenteronline.com/services/v2/service_types/{service_type[0]}/plans?offset={total_service_count-25}", auth=(username, password))
            now = datetime.now()
            now = now.strftime("%B %-d, %Y")
            now_year = datetime.now() #drop?
            now_year = now_year.strftime("%Y") #drop?
            if filter_for_today_only:
                service_list = service_list + [[service_type[0],p['id'],service_type_name+" - "+p['attributes']['dates']+" - "+str(p['attributes']['title'])] for p in service_page.json()['data'] if now in p['attributes']['dates']]
            elif filter_forward_days > 0:
                #service_list = service_list + [[service_type[0],p['id'],service_type_name+" - "+p['attributes']['dates']+" - "+str(p['attributes']['title'])] for p in service_page.json()['data'] if any(i in p['attributes']['dates'] for i in filter_forward_list)]
                service_list = service_list + [[service_type[0],p['id'],service_type_name+" - "+p['attributes']['dates']+" - "+str(p['attributes']['title'])] for p in service_page.json()['data'] if any(i in p['attributes']['sort_date'] for i in filter_forward_list)]
            elif filter_forward_days < 0: #depreciate?
                service_list = service_list + [[service_type[0],p['id'],service_type_name+" - "+p['attributes']['dates']+" - "+str(p['attributes']['title'])] for p in service_page.json()['data'] if any(i in p['attributes']['dates'] and now_year in p['attributes']['dates'] for i in filter_forward_list+["&"])]
            else:
                service_list = service_list + [[service_type[0],p['id'],service_type_name+" - "+p['attributes']['dates']+" - "+str(p['attributes']['title'])] for p in service_page.json()['data']]
            done = True
        except Exception as e:
            print(f"E: {e} (probably api rate limit)")
            time.sleep(5)
    plan_loading_count -= 1

#load plans
def reload_plans():
    print(color.GREEN, "LOADING PLANS", color.RESET)
    global plan_loading_count
    global service_list
    service_list = []
    global filter_forward_list
    #filter_forward_list = [(datetime.now() + timedelta(days=i)).strftime("%B %-d, %Y") for i in range(0, abs(filter_forward_days)) if filter_forward_days != 0]
    filter_forward_list = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-(filter_backward_days), abs(filter_forward_days)) if filter_forward_days != 0]
    print(f"FFL: {filter_forward_list}")
    for service_type in service_type_list:
        if threading_load_plans:
            print(f"STARTING THREAD FOR SERVICE TYPE: {service_type}")
            _thread.start_new_thread(load_plans_for_service_type, (service_type,))
        else:
            print(f"LOADING SERVICE TYPE: {service_type}")
            load_plans_for_service_type(service_type)
        time.sleep(0.025)
    while plan_loading_count > 0:
        print(f"loading... {plan_loading_count} left")
        time.sleep(0.3)

#show plans
def show_plans():
    counter = 1
    for i in service_list:
        print(f"{color.CYAN}{counter}: {color.GREEN}{i[2]}{color.RESET}")
        counter += 1

def print_help():
    print(f" HELP: {color.CYAN}\nL = live\nC = clear screen\nS = show plan(s)\nR = Reload plans\nU = update\nH = help\nSPLICER = configure app {color.RESET}")

def set_propresenter_stage_message_text(message):
    if propresenter_active == False:
        return
    message = f"\"{message}\""
    headers = {'Content-Type': 'application/json'}
    propresenter_timer_msg = requests.put(f"http://{propresenter_machine_ip}:{propresenter_machine_port}/v1/stage/message", data=message, headers=headers)

block = "█"
space = " "
b = block
s = space

letters = {
    "1": [
        [b, b],
        [b, b],
        [b, b],
        [b, b],
        [b, b]
    ],
    "2": [
       [b, b, b, b, b, b],
       [s, s, s, s, b, b],
       [b, b, b, b, b, b],
       [b, b, s, s, s, s],
       [b, b, b, b, b, b]
    ],
    "3": [
       [b, b, b, b, b, b],
       [s, s, s, s, b, b],
       [b, b, b, b, b, b],
       [s, s, s, s, b, b],
       [b, b, b, b, b, b]
    ],
    "4": [
       [b, b, s, s, b, b],
       [b, b, s, s, b, b],
       [b, b, b, b, b, b],
       [s, s, s, s, b, b],
       [s, s, s, s, b, b]
    ],
    "5": [
       [b, b, b, b, b, b],
       [b, b, s, s, s, s],
       [b, b, b, b, b, b],
       [s, s, s, s, b, b],
       [b, b, b, b, b, b]
    ],
    "6": [
       [b, b, b, b, b, b],
       [b, b, s, s, s, s],
       [b, b, b, b, b, b],
       [b, b, s, s, b, b],
       [b, b, b, b, b, b]
    ],
    "7": [
       [b, b, b, b, b, b],
       [s, s, s, s, b, b],
       [s, s, s, s, b, b],
       [s, s, s, s, b, b],
       [s, s, s, s, b, b]
    ],
    "8": [
       [b, b, b, b, b, b],
       [b, b, s, s, b, b],
       [b, b, b, b, b, b],
       [b, b, s, s, b, b],
       [b, b, b, b, b, b]
    ],
    "9": [
       [b, b, b, b, b, b],
       [b, b, s, s, b, b],
       [b, b, b, b, b, b],
       [s, s, s, s, b, b],
       [b, b, b, b, b, b]
    ],
    "0": [
       [b, b, b, b, b, b],
       [b, b, s, s, b, b],
       [b, b, b, b, b, b],
       [s, s, s, s, b, b],
       [b, b, b, b, b, b]
    ],
    ":": [
        [s, s],
        [b, b],
        [s, s],
        [b, b],
        [s, s]
    ],
    "-": [
        [s, s, s],
        [s, s, s],
        [b, b, b],
        [s, s, s],
        [s, s, s]
    ],
}

def blocktext(text, colorblock):
    split_text = list(text)
    output_list = ["", "", "", "", ""]
    for letter in split_text:
        for i in range(0, len(output_list)):
            output_list[i] = output_list[i]+''.join(colorblock+char if char == b else color.RESET+char for char in letters[letter][i])+color.RESET+s
    return "\n".join(output_list)

#init all variables that will become globals
service_type_id = 0
plan_id = 0
#rl = []
current_item = []
current_item_update_time = 0
other_items = []
other_items_update_time = 0
plan_times = []
plan_times_update_time = 0
time_remaining = 0
preservice_mode = 1
stale = 0
last_error = ""

#timing backend, contains all blocking API requests
def live_timing_back(service_type_id, plan_id):
    global current_item
    global current_item_update_time
    global other_items
    global other_items_update_time
    global plan_times
    global plan_times_update_time
    global stale
    global preservice_mode
    global last_error
    crashes = 0
    stale = 0
    print("BACKEND START")
    while True:
        try:
            current_item_time_data = requests.get(rl['data']['links']['current_item_time'], timeout=8, auth=(username, password))
            current_item_time_data = current_item_time_data.json()
            current_item_id = current_item_time_data['data']['relationships']['item']['data']['id']
            #print(current_item_time_data['data']['attributes']['live_start_at'])
            other_item_time_data = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/live/items/{current_item_id}", auth=(username, password), timeout=8)
            other_item_time_data = other_item_time_data.json()['data']['attributes']
            current_item = current_item_time_data
            other_items = other_item_time_data
            current_item_update_time = time.time()
            other_items_update_time = time.time()
            crashes = 0
            preservice_mode = 0
            stale = 0
            time.sleep(2)
        except Exception as e:
            print(f"E {e}")
            try: #check if in preservice
                try:
                    if rl['data']['links']['current_item_time'] != None: #if current item time shows up
                        print("CT/RL OK")
                    else:
                        print(0/0)
                except:
                    #print("RELOADING PLAN DATA (RL)")
                    rl = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/live", auth=(username, password))
                    rl = rl.json() #all after this will only be using json obect, not request code etc
                new_plan_times = []
                plan_times_count = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/plan_times", auth=(username, password), timeout=4)
                plan_times_count = plan_times_count.json()['meta']['total_count']
                for plan_times_offset in range(0, plan_times_count, 25): #load all plan time pages
                    r_plan_times = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/plan_times?offset={plan_times_offset}", auth=(username, password), timeout=4)
                    r_plan_times = r_plan_times.json()
                    new_plan_times = new_plan_times + [[i['attributes']['starts_at'], i['attributes']['name']] for i in r_plan_times['data']]
                plan_times = new_plan_times #separate variables needed bc loading time of requests
                swapped = True
                while swapped: #bubble sort plan times
                    swapped = False
                    for i in range(0, len(plan_times)-1):
                        if float(datetime.strptime(plan_times[i][0], "%Y-%m-%dT%H:%M:%SZ").timestamp()) > float(datetime.strptime(plan_times[i+1][0], "%Y-%m-%dT%H:%M:%SZ").timestamp()):
                            plan_times[i+1], plan_times[i] = plan_times[i], plan_times[i+1]
                            swapped = True
                plan_times_update_time = time.time()
                crashes = 0
                preservice_mode = 1
                stale = 0
                time.sleep(10 if time_remaining > 60 else 2)
            except Exception as e: #if PCO is legit down or if there is no internet
                crashes += 1
                stale += 1
                #print(f"CRASH: {e}")
                last_error = f"BACKEND ERROR {e}"
                time.sleep([crashes/2 if crashes < 16 else 8][0])

any_update_time = 0
#frontend, no blocking components except ProPresenter send
def live_timing_front():
    global any_update_time #needed?
    global time_remaining
    global stale
    global last_error
    print("FRONTEND START")
    set_propresenter_stage_message_text("T-START")
    time.sleep(2)
    stale = 0 #start stale at zero
    #preservice_mode = 1 #start in preservice mode unless first pass of Live API works
    while True:
        try:
            if preservice_mode != 0: #preservice mode
                time_until_next_service = plan_times
                today = date.today()
                plan_ok = 0
                time_remaining = 0
                service_time = ''
                for i in time_until_next_service:
                    service_time = i[0] #.split("T")[1][:-1] #for printing
                    service_time_name = i[1] #for printing
                    dt_object = datetime.strptime(i[0], "%Y-%m-%dT%H:%M:%SZ")
                    dt_unix = dt_object.timestamp()
                    time_difference = (dt_unix-time.time()) + datetime.now().astimezone().utcoffset().total_seconds() + preroll_offset
                    if time_difference > 0:
                        time_remaining = int(round(time_difference, 0))
                        time_remaining_min, time_remaining_sec = divmod(time_remaining, 60)
                        time_remaining_sec = [int(round(time_remaining_sec, 0)) if time_remaining_sec > 9 else "0"+str(int(round(time_remaining_sec, 0)))][0]
                        #print(f"NEXT SERVICE TIME: {i[1]}")
                        plan_ok = 1
                        break
                if plan_ok == 0:
                    print(f"{color.RED}NO SERVICE TIME MATCH{color.RESET}")
                    stale += 80
                    set_propresenter_stage_message_text("NO SERVICE")
                    time.sleep(1)
                    continue
                os.system("clear")
                #print time data
                print(blocktext(f"{time_remaining_min}:{time_remaining_sec}", color.YELLOW+color.BK_YELLOW)+color.RESET)#, end="", flush=True)
                if data_display:
                    c = "\n".join(current_plan_name.split("-"))
                    print(f"{color.BOLD}{color.CYAN}{c}{color.RESET}")
                    print(f"{color.BOLD}COMPUTER NAME: {color.CYAN}{system_name}{color.RESET}")
                    print(f"{color.YELLOW}{color.BOLD}----------P/S---------{color.RESET}")
                    print(f"{color.MAGENTA}NEXT TIME: {color.RESET}{color.RED if time_remaining < 0 else ''}{service_time}Z")                                                                                                                              
                    print(f"{color.MAGENTA}TIME NAME: {color.RESET}{service_time_name}")
                time.sleep(0.8)
            elif preservice_mode == 0: #service mode
                current_item_time_data = current_item
                other_item_time_data = other_items
                live_start_time = current_item_time_data['data']['attributes']['live_start_at']
                today = date.today()
                dt_object = datetime.strptime(live_start_time, "%Y-%m-%dT%H:%M:%SZ")
                dt_unix = dt_object.timestamp()
                time_offset = float(current_item_time_data['data']['attributes']['length_offset'])/1000 #pco gives offset in ms
                time_elapsed = dt_unix-time.time() #account for time offset
                time_elapsed += datetime.now().astimezone().utcoffset().total_seconds() #account for UTC
                time_elapsed = round(abs(time_elapsed), 0) #round time elapsed
                time_remaining = round((other_item_time_data['length']-time_elapsed)+time_offset, 1) #calc and round time remaining
                time_remaining_min, time_remaining_sec = divmod(abs(time_remaining), 60) #split time remaining to min/sec
                time_remaining_min = int(round(time_remaining_min, 0)) #round time remaining (not needed?)
                time_remaining_sec = [int(round(time_remaining_sec, 0)) if time_remaining_sec > 9 else "0"+str(int(round(time_remaining_sec, 0)))][0]
                flag = [color.RED if time_remaining < 0 else color.GREEN][0] #green text if on time, red if behind
                os.system("clear")
                #print time data
                print(blocktext(f"{'-' if time_remaining < 0 else ''}{time_remaining_min}:{time_remaining_sec}", flag+color.BK_GREEN if flag == color.GREEN else flag+color.BK_RED))
                print(f"{other_item_time_data['title'].center(28)}{color.RESET}")
                if data_display:
                    print(f"{color.BOLD}COMPUTER NAME: {color.CYAN}{system_name}{color.RESET}")
                    print(f"{color.BOLD}{flag}TIME ELAPSED:", time_elapsed)
                    print(f"TIME ITEM:", other_item_time_data['length'])
                    print(f"TIME OFFSET:", time_offset, color.RESET)
                    for i in other_item_time_data:
                        print([color.UNDERLINE+i+color.RESET+color.BLUE+" "+other_item_time_data[i]+"\n"+color.RESET if "ti" in i and other_item_time_data[i] != None else ''][0], end='', flush=True)                                                                          
                    print(f"\n{[color.RED+str(stale)+color.RESET if stale > 15 else stale][0]} - {last_error}")
            time_string = f"{'-' if time_remaining < 0 else ''}{time_remaining_min}:{time_remaining_sec}{' - '+service_time_name if preservice_mode != 0 and service_time_name != None else ''}"
            set_propresenter_stage_message_text(time_string if stale < 70 else "NO PCO")
            # with open("time.json", "w") as timefile:
            #     s = "{ \"time\""+f": \"{time_string}\" "+"}"
            #     timefile.write(f"{s}\n")
            time.sleep(0.2)
        except Exception as e:
            #print(f"TIMING FRONTEND ERROR: {e}")
            last_error = f"FRONTEND ERROR {e}"
            stale += 50
            time.sleep(1)
            continue


if __name__ == '__main__':
    load_service_types()
    time.sleep(1.5)
    reload_plans()
    time.sleep(0.5)
    os.system("clear")
    show_plans()
    while True:
        try:
            c = input("> ")
            c = c.split(" ")
            c[0] = c[0].upper() #make first letter command uppercase
            if len(c) > 1: #stop if it isn't a multiple letter command or if they just hit enter
                if c[0] == "S": #list a specific plans contents
                    i = service_list[int(c[1])-1]
                    print(f"{color.CYAN}{c[1]}: {color.RESET}{i[0]} - {i[1]} - {color.GREEN}{i[2]}{color.RESET}")
                    continue
                if c[0] == "L": #live
                    service_type_id = service_list[int(c[1])-1][0]
                    plan_id = service_list[int(c[1])-1][1]
                    current_plan_name = service_list[int(c[1])-1][2]
                    print(service_type_id)
                    print(plan_id)
                    plan_ok = 0
                    while plan_ok == 0:
                        rl = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/live", auth=(username, password))
                        #print(rl.json())
                        rl = rl.json() #all after this will only be using json obect, not request code etc
                        try:
                            for i in rl['data']['links']:
                                print(i, color.BLUE, rl['data']['links'][i], color.RESET)
                            plan_ok = 1
                        except Exception as e:
                            print("plan looks funny, reloading (plan is broken PCO sent garbage)")
                            time.sleep(3)
                    print(color.GREEN+"PROPRESENTER ACTIVE"+color.RESET if propresenter_active else "PROPRESENTER DISABLED")
                    #plan_time_static_offset = int([i[1] for i in service_type_list if i[0] == service_type_id][0])
                    #attempted multithreading
                    t1 = _thread.start_new_thread(live_timing_back, (service_type_id, plan_id,))
                    t2 = _thread.start_new_thread(live_timing_front, ())
                continue #so can have second handlers for each letter than only run when no args
            elif c[0] == "K":
                set_propresenter_stage_message_text("RLS")
                print("EXITING")
                sys.exit()
            elif c[0] == "C": #clear the screen
                os.system("clear")
            elif c[0] == "R": #reload plans
                reload_plans()
                show_plans()
            elif c[0] == "S": #refresh plans and print them to the screen
                show_plans()
            elif c[0] == "SPLICER":
                configure(configure_map)
            elif c[0] == "L":
                print("Live: Select plan (ex. L 1)")
            elif c[0] == "U":
                update()
            elif c[0] == "H": #print the help menu
                print_help()
        except KeyboardInterrupt:
            set_propresenter_stage_message_text("RLS")
            print("EXITING")
            sys.exit(0)
        except Exception as e: #if anything throws an err
            print("ERR", e)

#!/usr/bin/python3
#v-idk
import os
import sys
sys.dont_write_bytecode = True
import subprocess
try:
    import requests
except:
    os.system("pip3 install requests")
    import requests
import json
import time
import random
from datetime import datetime, date, timedelta
import _thread
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

# Restart and reload code from file
def restart():
    sys.stdout.flush() 
    sys.stderr.flush()
    os.execv(sys.executable, ['python3'] + sys.argv)

# Load settings from pco_config.json, first in hidden file in home folder,
# then in local folder, then load from GitHub if not found
try:
    with open(os.path.expanduser("~")+"/.pco_config.json", "r") as file:
        cfg = json.load(file)
except Exception as e:
    try:
        with open("pco_config.json", "r") as file:
            print("LOADING LOCAL CONFIG FILE (NONSTANDARD LOCATION)")
            cfg = json.load(file)
    except:
        print(f"NO CONFIG FILE FOUND, DOWNLOADING TEMPLATE {e}")
        os.system(f"wget -O {os.path.expanduser('~')+'/.pco_config.json'} https://raw.githubusercontent.com/K-256/planning_center_thingy/refs/heads/main/pco_config.json")
        time.sleep(2)
        restart()

print(cfg)

# Check if PCO API tokens not set from defaults
username = "REPLACE_WITH_YOUR_TOKENS_ETC_FROM_PCO_DEV_PAGE"
    print("PCO API TOKEN NOT SET, SET IN ~/.pco_config.json")
    sys.exit(99)

username = cfg['username']
password = "REPLACE_WITH_YOUR_TOKENS_ETC_FROM_PCO_DEV_PAGE"

service_type_list = []


webdisplay_html_string = """
<head>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,100..900;1,100..900&family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Roboto:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">

<style>
body {
    background-color: #1F242A;
    color: white;
    font-family: Noto Sans;
    margin: 0;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1px
}

.center-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

p {
  margin: 0;
}

</style>
</head>
<body>

<div class="center-container">
  <p style="font-size: 60px" id="current-time-name">-</p>
  <p style="font-size: 165px" id="time">-</p>
  <p style="font-size: 60px" id="next-time-name">-</p>
</div>

<script>

  const timecolor = document.getElementById("time");

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function reload_page_thingy() {
    const current_URL = window.location.href.split('?')[0];
    const reload_URL = current_URL + '?jumpCache=' + new Date().getTime()
    window.location.reload(reload_URL);
  }
  
  async function time_display() {
    while (true) {
      try {
        req = await fetch("/time.json");
        if (!req.ok) {
          console.error("REQUEST FAILED");
          await sleep(2000);
          reload_page_thingy();
        }
        const data = await req.json();
        document.getElementById("time").innerHTML = data.time;
        document.getElementById("current-time-name").innerHTML = data.current_item_name;
        document.getElementById("next-time-name").innerHTML = data.next_item_name;
        console.log("DATA: ", data);
        if (data.time.startsWith("-")) {
          timecolor.style.color = "red";
        } else {
          timecolor.style.color = "white"
        }
      } catch (error) {
        console.error('JSON fetch thingy failed: ', error);
      }
      await sleep(500);
    }
  }

  time_display();

</script>

</body>
"""

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

def update():
    print(f"{color.GREEN}--UPDATING--{color.RESET}")
    try:
        t = 0
        print(1/t)
    except:
        print(f"{color.BLUE}--UPDATING FROM GITHUB--{color.RESET}")
        os.system(f"curl -L -o {__file__} https://githubusercontent.com/K-256/planning_center_thingy/glassrock.py")
    print(f"{color.RED}--RESTARTING--{color.RESET}")
    time.sleep(1)
    restart()

def clear():
    if not cfg['disable_clear']:
        os.system("clear")

def configure():
    clear()
    print(color.YELLOW+color.BOLD+"------CONFIGURE------", color.RESET)
    print(color.YELLOW+"   (CTRL+X to save/exit)", color.RESET)
    time.sleep(4)
    subprocess.run(["nano", f"{os.path.expanduser('~')}/.pco_config.json"])
    print(f"{color.GREEN}FINISHED CONFIGURATION, RESETTING{color.RESET}")
    time.sleep(1)
    restart()
    
def load_service_types():
    print(f"{color.BLUE}LOADING SERVICE TYPES{color.RESET}")
    global service_type_list
    service_type_list = []
    service_type_page = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types?where[name]={cfg['campus_name']}&per_page=100", auth=(username, password))
    service_type_list = service_type_list + [[service_type['id'], 0, service_type['attributes']['name']] for service_type in service_type_page.json()['data'] if cfg['campus_name'] in service_type['attributes']['name']]

plan_loading_count = 0
def load_plans_for_service_type(service_type):
    done = False
    global plan_loading_count
    global service_list
    plan_loading_count += 1
    while not done:
        try:
            print(f"LOADING SERVICE TYPE: {color.BLUE}{service_type[0]}{color.RESET}")
            total_service_count = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type[0]}/plans?offset=9999", auth=(username, password), timeout=4)
            total_service_count = int(total_service_count.json()['meta']['total_count'])
            print(f"SERVICE COUNT: {color.CYAN}{total_service_count}{color.RESET}")
            service_type_name = service_type[2]
            print(f"SERVICE TYPE NAME: {color.CYAN}{service_type_name}{color.RESET}")
            service_page = requests.get(f"http://api.planningcenteronline.com/services/v2/service_types/{service_type[0]}/plans?offset={total_service_count-25}", auth=(username, password), timeout=4)
            now = datetime.now()
            now = now.strftime("%B %-d, %Y")
            #now_year = datetime.now() #drop?
            #now_year = now_year.strftime("%Y") #drop?
            if cfg['filter_for_today_only']:
                service_list = service_list + [[service_type[0],p['id'],service_type_name+" - "+p['attributes']['dates']+" - "+str(p['attributes']['title'])] for p in service_page.json()['data'] if now in p['attributes']['dates']]
            elif cfg['filter_forward_days'] > 0:
                #service_list = service_list + [[service_type[0],p['id'],service_type_name+" - "+p['attributes']['dates']+" - "+str(p['attributes']['title'])] for p in service_page.json()['data'] if any(i in p['attributes']['dates'] for i in filter_forward_list)]
                service_list = service_list + [[service_type[0],p['id'],service_type_name+" - "+p['attributes']['dates']+" - "+str(p['attributes']['title'])] for p in service_page.json()['data'] if any(i in p['attributes']['sort_date'] for i in filter_forward_list)]
            elif cfg['filter_forward_days'] < 0: #depreciate?
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
    filter_forward_list = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-(cfg['filter_backward_days']), abs(cfg['filter_forward_days'])) if cfg['filter_forward_days'] != 0]
    print(f"FFL: {filter_forward_list}")
    for service_type in service_type_list:
        if cfg['threading_load_plans']:
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
    if cfg['propresenter_active'] == False:
        return
    message = f"\"{message}\""
    headers = {'Content-Type': 'application/json'}
    propresenter_timer_msg = requests.put(f"http://{cfg['propresenter_machine_ip']}:{cfg['propresenter_machine_port']}/v1/stage/message", data=message, headers=headers)

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
       [b, b, s, s, b, b],
       [b, b, s, s, b, b],
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

#init all variables that will become globals (PCO section)
# service_type_id = 0
# plan_id = 0
current_item = ""
current_item_update_time = 0
next_item_name = ""
other_items = []
other_items_update_time = 0
plan_times = []
plan_times_update_time = 0
service_items = {}

preroll_offset = int(cfg['preroll_offset_default'])
time_remaining = 0
preservice_mode = 1

last_error = ""
current_timejson = ""
fast_speed = False

#init HyperDeck control variables
hyperdeck_control = 0 # 0 is stop, 1 is record
hyperdeck_state = {} # state dict for hyperdecks
time_since_service_stop = 0

def hyperdeck_interface(hyperdeck_ip, hyperdeck_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sigmasock:
        print(f"CONNECTING TO HYPERDECK {hyperdeck_ip} port {hyperdeck_port}")
        sigmasock.connect((hyperdeck_ip, hyperdeck_port))
        print("connected")
        internal_state = "unknown"
        time.sleep(2)
        while True:
            command = "transport info\n"
            sigmasock.sendall(command.encode('utf-8'))
            response = sigmasock.recv(4096)
            r = response.decode('utf-8')
            r = r.split("\n")
            if "208 transport info" in r[0]:
                hyperdeck_state[hyperdeck_ip] = r[1][:-1]
                if hyperdeck_control == 1 and "record" not in r[1]:
                    sigmasock.sendall("record\n".encode('utf-8'))
                if hyperdeck_control == 0 and "record" in r[1]:
                    sigmasock.sendall("stop\n".encode('utf-8'))
            else:
                hyperdeck_state[hyperdeck_ip] = "unknown"
            time.sleep(1)

#timing backend, contains all blocking API requests
def live_timing_back(service_type_id, plan_id):
    global current_item
    global current_item_update_time
    global next_item_name
    global other_items
    global other_items_update_time
    global plan_times
    global plan_times_update_time
    global preservice_mode
    global last_error
    global time_since_service_stop
    global hyperdeck_control
    global service_items
    current_item_id = 0
    crashes = 0
    print("BACKEND START")
    while True:
        try: #there may be something triggering an error in this block?
            current_item_time_data = requests.get(rl['data']['links']['current_item_time'], timeout=8, auth=(username, password))
            current_item_time_data = current_item_time_data.json()
            current_item_id_new = current_item_time_data['data']['relationships']['item']['data']['id']
            if current_item_id_new != current_item_id:
                current_item_id = current_item_id_new
                next_item_id = requests.get(rl['data']['links']['next_item_time'], timeout=8, auth=(username, password))
                next_item_id = next_item_id.json()['data']['relationships']['item']['data']['id']
                next_item_name = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/live/items/{next_item_id}", auth=(username, password), timeout=8)
                next_item_name = next_item_name.json()['data']['attributes']['title']
            #print(current_item_time_data['data']['attributes']['live_start_at'])
            other_item_time_data = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/live/items/{current_item_id}", auth=(username, password), timeout=8)
            other_item_time_data = other_item_time_data.json()['data']['attributes']
            current_item = current_item_time_data
            other_items = other_item_time_data
            current_item_update_time = time.time()
            other_items_update_time = time.time()
            crashes = 0
            preservice_mode = 0
            time_since_service_stop = 0
            time.sleep(1.5)
        except Exception as e:
            last_error = f"BACKEND STAGE 1 ERROR - {e}"
            try: #check if in preservice
                #check if rl data is useable
                try:
                    #needs a try except to catch rl not actually existing
                    if rl['data']['links']['current_item_time'] != None: #if current item time shows up
                        #needs if bc sometimes rl is blank
                        print("CT/RL OK")
                    else:
                        print(0/0)
                except:
                    #reload rl data if not good
                    print("RELOADING RL")
                    rl = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/live", auth=(username, password))
                    rl = rl.json() #all after this will only be using json obect, not request code etc
                new_plan_times = []
                plan_times_count = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/plan_times", auth=(username, password), timeout=4)
                plan_times_count = plan_times_count.json()['meta']['total_count']
                # Load all plan time pages
                for plan_times_offset in range(0, plan_times_count, 25):
                    r_plan_times = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/plan_times?offset={plan_times_offset}", auth=(username, password), timeout=4)
                    r_plan_times = r_plan_times.json()
                    new_plan_times = new_plan_times + [[i['attributes']['starts_at'], i['attributes']['name']] for i in r_plan_times['data'] if i['attributes']['time_type'] != "other"]
                plan_times = new_plan_times #separate variables needed bc loading time of requests
                # Bubble sort plan times
                swapped = True
                while swapped:
                    swapped = False
                    for i in range(0, len(plan_times)-1):
                        if float(datetime.strptime(plan_times[i][0], "%Y-%m-%dT%H:%M:%SZ").timestamp()) > float(datetime.strptime(plan_times[i+1][0], "%Y-%m-%dT%H:%M:%SZ").timestamp()):
                            plan_times[i+1], plan_times[i] = plan_times[i], plan_times[i+1]
                            swapped = True
                # next_item_time = ""
                plan_times_update_time = time.time()
                preservice_mode = 1
                time_since_service_stop += 10 if time_remaining > 60 else 1
                time.sleep(10 if time_remaining > 60 else 1)
            except Exception as e: #if PCO is legit down or if there is no internet
                last_error = f"BACKEND ERROR {e}"
                time.sleep([crashes/2 if crashes < 16 else 8][0])

any_update_time = 0
#frontend, no blocking components except ProPresenter send
def live_timing_front():
    global any_update_time #needed?
    global time_remaining
    global last_error
    global current_timejson
    global service_items
    global next_item_name
    global service_time_name
    global hyperdeck_control
    previous_t = ""
    print("FRONTEND START")
    set_propresenter_stage_message_text("T-START")
    time.sleep(2)
    #preservice_mode = 1 #start in preservice mode unless first pass of Live API works
    while True:
        # try:
        if True:
            if preservice_mode != 0: #preservice mode
                time_until_next_service = plan_times
                today = date.today()
                plan_ok = 0
                time_remaining = 0
                service_time = ''
                # Check all service times
                for i in time_until_next_service:
                    service_time = i[0] #.split("T")[1][:-1] #for printing
                    service_time_name = i[1] #for printing
                    current_item_name = service_time_name
                    next_item_name = service_time_name
                    dt_object = datetime.strptime(i[0], "%Y-%m-%dT%H:%M:%SZ")
                    dt_unix = dt_object.timestamp()
                    time_difference = (dt_unix-time.time()) + datetime.now().astimezone().utcoffset().total_seconds()
                    time_difference = time_difference - preroll_offset
                    #(cfg['preroll_offset'] if dt_object.weekday() in cfg['preroll_offset_days'] else 0)
                    # If found time is in the future
                    if time_difference > 0:
                        time_remaining = int(round(time_difference, 0))
                        time_remaining_min, time_remaining_sec = divmod(time_remaining, 60)
                        time_remaining_sec = [int(round(time_remaining_sec, 0)) if time_remaining_sec > 9 else "0"+str(int(round(time_remaining_sec, 0)))][0]
                        #print(f"NEXT SERVICE TIME: {i[1]}")
                        plan_ok = 1
                        break
                # HyperDeck triggers
                if time_remaining < cfg['hyperdeck_trigger_pre']+preroll_offset and service_time_name == None:
                    # if past hyperdeck trigger point and an actual service time
                    hyperdeck_control = 1
                if time_since_service_stop > cfg['hyperdeck_trigger_post']:
                    # If been longer than trigger tail stop hyperdecks
                    hyperdeck_control = 0
                # if plan not OK then show no service message
                if plan_ok == 0:
                    t = f"{color.RED}NO SERVICE TIME MATCH{color.RESET}"
                    time_remaining_min = 0
                    time_remaining_sec = 0
                    time_remaining = 0
                    set_propresenter_stage_message_text("NO SERVICE")
                else:
                    #print normal time data only if plan good
                    # if cfg['blockprint']:
                    t = blocktext(f"{time_remaining_min}:{time_remaining_sec}", color.YELLOW+color.BK_YELLOW) if cfg['blockprint'] else ''
                    t = f"{color.YELLOW}{time_remaining_min}:{time_remaining_sec}{color.RESET}" if not cfg['blockprint'] else t
                    t += f"\n{color.BLUE+"\n".join(current_plan_name.split("-"))+color.RESET}\n"
                    t += f"{color.BOLD}COMPUTER: {color.CYAN}{system_name}{color.RESET}\n"
                    t += f"{color.YELLOW}{color.BOLD}----------P/S---------{color.RESET}\n"
                    t += f"{color.MAGENTA}NEXT TIME: {color.RESET}{service_time}\n"
                    t += f"{color.MAGENTA}TIME NAME: {color.RESET}{service_time_name}\n"
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
                #print time data
                if cfg['blockprint']:
                    t = blocktext(f"{'-' if time_remaining < 0 else ''}{time_remaining_min}:{time_remaining_sec}", flag+color.BK_GREEN if flag == color.GREEN else flag+color.BK_RED)
                else:
                    t = f"{color.BOLD}{color.UNDERLINE}{flag}TIME REM:"+f"{'-' if time_remaining < 0 else ''}{time_remaining_min}:{time_remaining_sec}{color.RESET}\n".rjust(16)
                    t += f"{flag}TIME ELAPSED: "+f"{time_elapsed}{color.RESET}\n".rjust(11)
                    t += f"{flag}TIME ITEM: "+f"{other_item_time_data['length']}{color.RESET}\n".rjust(14)
                    t += f"{flag}TIME OFFSET: "+f"{time_offset}{color.RESET}\n".rjust(12)
                    t += f"ITEM TITLE: "+f"{current_item_name}{color.RESET}\n".rjust(14)
                    t += f"{color.BOLD}COMPUTER: {color.CYAN}{system_name}{color.RESET}\n"
                hyperdeck_control = 1 if hyperdeck_control != 1 else hyperdeck_control #set hyperdeck control if not already set
                current_item_name = other_item_time_data['title']
            t += f"\n - HYPERDECK - \n{"\n".join(i+" - "+hyperdeck_state[i] for i in hyperdeck_state)}" if cfg['hyperdeck_control_enable'] else ''
            t += f"\nHDC: {hyperdeck_control} - TSS: {time_since_service_stop} - HDT: {preroll_offset}+{cfg['hyperdeck_trigger_pre']}" if cfg['hyperdeck_control_enable'] else ''
            t += f"\n\n{last_error} - {last_error}" if cfg['show_last_error'] else ''
            if t != previous_t:
                clear()
                print(t)
                time_string = f"{'-' if time_remaining < 0 else ''}{time_remaining_min}:{time_remaining_sec}{' - '+service_time_name if preservice_mode != 0 and service_time_name != None else ''}"
                set_propresenter_stage_message_text(time_string)
                current_timejson = f"{{ \"time\": \"{'-' if time_remaining < 0 else ''}{time_remaining_min}:{time_remaining_sec}\", \"current_item_name\": \"{current_item_name}\", \"next_item_name\": \"{next_item_name}\"}} "
            previous_t = t
            time.sleep(0.2)
        # except Exception as e:
        #     last_error = f"FRONTEND ERROR {e}"
        #     print(last_error)
        #     time.sleep(1)
        #     continue

class request_handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if len(args) > 1 and args[1].startswith(('4', '5')):
            super().log_message(format, *args) # Only print client/server errors
    def do_GET(self):
        if self.path == '/time.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(current_timejson.encode())
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(webdisplay_html_string.encode('utf-8'))

def server(port=6767):
    server_address = ('', port)
    httpd = HTTPServer(server_address, request_handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("EXITING")
        httpd.server_close()


if __name__ == '__main__':
    load_service_types()
    time.sleep(1.5)
    reload_plans()
    time.sleep(0.5)
    clear()
    if cfg['web_display']:
            _thread.start_new_thread(server, (cfg['web_display_port'],))
            print(" WEBDISPLAY ENABLED")
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
                    # Get Preroll offset time
                    service_items = requests.get(f"https://api.planningcenteronline.com/services/v2/service_types/{service_type_id}/plans/{plan_id}/live/items", auth=(username, password), timeout=8)
                    service_items = service_items.json()['data']
                    for item in service_items:
                        # print(item)
                        if item['attributes']['service_position'] == "pre":
                            preroll_offset = float(item['attributes']['length'])
                            print(f"LOADED PREROLL OFFSET OF {color.BLUE}{preroll_offset}{color.RESET} FROM ITEM {color.BLUE}{item['attributes']['title']}{color.RESET}")
                            break
                    time.sleep(2)
                    #attempted multithreading
                    t1 = _thread.start_new_thread(live_timing_back, (service_type_id, plan_id,))
                    t2 = _thread.start_new_thread(live_timing_front, ())
                    if cfg['hyperdeck_control_enable']:
                        for ip in cfg['hyperdeck_ip_list']:
                            _thread.start_new_thread(hyperdeck_interface, (ip, cfg['hyperdeck_port']))
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
            elif c[0] == "X":
                configure()
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

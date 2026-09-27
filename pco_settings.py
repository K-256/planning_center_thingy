# Configuration file for PCO clock
cfg = {
    # PCO API username
    "username": "REPLACE_WITH_YOUR_TOKEN",
    # PCO API password
    "password": "REPLACE_WITH_YOUR_TOKEN",
    # CAMPUS NAME or search term for filtering plans
    "campus_name": "PSL |",
    #service_type_list = []
    # Time to move back service start
    "preroll_offset": -123,
    # Days (int, starting from 0=Monday) to use preroll_offset
    "preroll_offset_days": [6],
    # Enable ProPresnter API send
    "propresenter_active": False,
    #ProPresenter machine IP (should be 127.0.0.1 if this computer)
    "propresenter_machine_ip": "127.0.0.1",
    #ProPresenter HTTP API port
    "propresenter_machine_port": "1025",
    #filter for only plans happening today
    "filter_for_today_only": False,
    #how many days to look forward for plans
    "filter_forward_days": 6,
    #how many days to look backward for plans
    "filter_backward_days": 1,
    #multithread plans load as one thread per plan type
    "threading_load_plans": True,
    #blockprint (being depreciated)
    "blockprint": True,
    #show all info instead of just time+item_name
    "data_display": True,
    #write time info to timejson file
    "file_timejson_output": False,
    #enable web display
    "web_display": True,
    #web display port
    "web_display_port": 6768
    # #skip telemetry webhook url
    # "telemetry_enable": true, #skip
    # "telemetry_webhook_url": "https://discord.com/api/webhooks/1428075539427758100/yinvtugnj6hmmrirm-vumhzkb4jh4yerlveb0cydpmv4doljiqgv1efrddacfccihqpi" #skip
}

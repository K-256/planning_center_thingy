# planning_center_thingy
Planning Center Live CLI Tool

# Config options
- 1. `username` set to token username generated in PCO Developer site
- 2. `password` set to token password generated in PCO Developer site
- 3. `campus_name` set to campus name text to filter for plans by
- 4. `preroll_offset` offset from actual service time to preroll start
- 5. `preroll_offset_days` days of the week to enable preroll offset for (int, Monday = 0)
- 6. `propresenter_active` enable ProPresenter API send
- 7. `propresenter_machine_ip` IP addr or hostname (or 127.0.0.1) of ProPresenter computer
- 8. `propresenter_machine_port` ProPresenter machine HTTP API port (found in network settings)
- 9. `filter_for_today_only` Only show plans happening today (overrides filter forward/backward)
- 10. `filter_forward_days` How many days forward to look for plans
- 11. `filter_backward_days` How many days backward to loo for plans
- 12. `threading_load_plans` Enable loading plans with multithreading
- 13. `blockprint` Use block numbers (probably being removed soon)
- 14. `data_display` Show other information besides time remaining in item
- 15. `file_timejson_output` Write time data to time.json file (probably being removed soon)
- 16. `web_display` Enable builtin web server for time display
- 17. `web_display_port` Port to host web display on
- run commands
  - Commands:
    - `L` - Connect to PCO live
    - `S` - Show loaded plans
    - `K` - Stop running PCO live plan and exit
    - `R` - Reload plans
    - `X` - open config file

# ProPresenter API Connection
- Enable in ProPresenter settings (under "network")
- Set machine ip and port in pco_config.json to match
- Make sure your stage display has a text box that shows the stage mesage
# Why is it called glass rock?
- A glass rock looks cool and if you drop it, it explodes

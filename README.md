# planning_center_thingy
Planning Center Live CLI Tool

# CONFIG OPTIONS
- 1. `username` set to token username generated in PCO Developer site
- 2. `password` set to token password generated in PCO Developer site
- 3. `campus_name` set to campus name text to filter for plans by
- 4. `preroll_offset_default` default offset from actual service time if no 'pre' item found
- 5. `propresenter_active` enable ProPresenter API send
- 6. `propresenter_machine_ip` IP addr or hostname (or 127.0.0.1) of ProPresenter computer
- 7. `propresenter_machine_port` ProPresenter machine HTTP API port (found in network settings)
- 8. `filter_for_today_only` Only show plans happening today (overrides filter forward/backward)
- 9. `filter_forward_days` How many days forward to look for plans
- 10. `filter_backward_days` How many days backward to loo for plans
- 11. `threading_load_plans` Enable loading plans with multithreading
- 12. `blockprint` Use block numbers (probably being removed soon)
- 13. `other_items_display` Show other information besides time remaining in item
- 14. `web_display` Enable builtin web server for time display
- 15. `web_display_port` Port to host web display on
- 16. `disable_clear` Disable clear command (for debugging)
- 17. `hyperdeck_control_enable` Enable Hyperdeck network control
- 18. `hyperdeck_port` Hyperdeck network control port (should be 9993)
- 19. `hyperdeck_trigger_pre` Seconds before 1st item time to start recording (stacks with preroll offset)
- 20. `hyperdeck_trigger_post` Seconds after PCO stops to stop recording
- 21. `hyperdeck_trigger_days` Days to use hyperdeck control (not built yet)
- 22. `show_last_error` Put debugging message containing most recent error at bottom of print

# RUN COMMANDS
- `L` - Connect to PCO live
- `S` - Show loaded plans
- `K` - Stop running PCO live plan and exit
- `R` - Reload plans
- `X` - open config file

# ProPresenter API Connection
- Enable in ProPresenter settings (under "Network" box)
- Set machine IP and port in pco_config.json to match
  - NOTE: can set IP to 127.0.0.1 if on the computer running ProPresenter
- Make sure your stage display has a text box that shows the stage message

# BlackMagic Hyperdeck connection
- Enable network remote control in settings
  - NOTE: you can do this remotely through the TCP connection
  - [BlackMagic Hyperdeck Ethernet API doc](https://documents.blackmagicdesign.com/DeveloperManuals/HyperDeckEthernetProtocol.pdf)
- Set Hyperdeck IP addresses in the pco_config.json file

# Why is it called glass rock?
- A glass rock looks cool and if you drop it, it explodes

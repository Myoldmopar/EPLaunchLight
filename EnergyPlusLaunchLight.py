import os

import gtk

from EPLaunchLight.EPLaunchLightWindow import EPLaunchLightWindow
from EPLaunchLight.Settings import load_settings, save_settings

# once done doing any preliminary processing, actually run the application
this_settings_file_name = os.path.join(os.path.expanduser("~"), ".eplaunchlight.json")

# we will keep the form in a loop to handle requested restarts (language change, etc.)
running = True
while running:
    this_settings = load_settings(this_settings_file_name)
    main_window = EPLaunchLightWindow(this_settings)
    gtk.main()
    save_settings(main_window.settings, this_settings_file_name)
    running = main_window.doing_restart
    main_window.destroy()

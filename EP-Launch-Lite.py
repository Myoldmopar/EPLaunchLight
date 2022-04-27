import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from EPLaunchLite import VERSION_STRING
from EPLaunchLite.EPLaunchLiteWindow import Window
from EPLaunchLite.Settings import load_settings, save_settings

# once done doing any preliminary processing, actually run the application
this_settings_file_name = os.path.join(os.path.expanduser("~"), f".eplaunchlite{VERSION_STRING}.json")

# we will keep the form in a loop to handle requested restarts (language change, etc.)
running = True
while running:
    this_settings = load_settings(this_settings_file_name)
    main_window = Window(this_settings)
    Gtk.main()
    save_settings(main_window.settings, this_settings_file_name)
    running = main_window.doing_restart
    main_window.destroy()

import os
from pathlib import Path
from sys import argv

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from EPLaunchLite.EPLaunchLiteWindow import Window
from EPLaunchLite.Settings import load_settings, save_settings, Keys

# once done doing any preliminary processing, actually run the application
this_settings_file_name = os.path.join(os.path.expanduser("~"), ".eplaunchlite.json")

# we will keep the form in a loop to handle requested restarts (language change, etc.)
running = True
while running:
    this_settings = load_settings(this_settings_file_name)
    if len(argv) > 1:
        this_settings[Keys.install_root] = Path(argv[1])
    main_window = Window(this_settings)
    Gtk.main()
    save_settings(main_window.settings, this_settings_file_name)
    running = main_window.doing_restart
    main_window.destroy()

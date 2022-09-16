import os

from EPLaunchLite import VERSION_STRING
from EPLaunchLite.EPLaunchLiteWindow import Window
from EPLaunchLite.Settings import load_settings, save_settings

this_settings_file_name = os.path.join(os.path.expanduser("~"), f".eplaunchlite{VERSION_STRING}.json")
this_settings = load_settings(this_settings_file_name)
main_window = Window(this_settings)
main_window.root.mainloop()
save_settings(main_window.settings, this_settings_file_name)

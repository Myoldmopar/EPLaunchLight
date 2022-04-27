import os
from platform import system
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject

from EPLaunchLite.EnergyPlusPath import EnergyPlusPathManager
from EPLaunchLite.EnergyPlusThread import EnergyPlusThread
from EPLaunchLite.FileTypes import FileTypes
from EPLaunchLite.International import translate as _, Languages, set_language
from EPLaunchLite.Settings import Keys


__program_name__ = "EP-Launch-Lite (v2.1)"


class Window(Gtk.Window):
    """
    This class is the main window class for EP-Launch-Lite
    """

    def __init__(self, settings):
        """
        This initializer function creates instance variables, sets up threading, and builds the GUI
        """

        # initialize the parent class
        super().__init__()

        # this flag will be used to trigger a restart from the calling manager
        self.doing_restart = False

        # initialize some class-level "constants"
        self.box_spacing = 4

        # initialize instance variables to be set later
        self.input_file_path = None
        self.weather_file_path = None
        self.eplus_install_path = Gtk.Entry()
        self.button_sim = None
        self.button_cancel = None
        self.ep_run_folder = None
        self.running_simulation_thread = None
        self.status_bar = None
        self.status_bar_context_id = None
        self.ep_version_label = Gtk.Label()
        self.edit_idf_button = None
        self.eplus_path_manager = None

        # try to load the settings very early since it includes initialization
        self.settings = settings

        # set the language early so the GUI building process reflects the desired language
        set_language(self.settings[Keys.language])

        # prepare threading
        GObject.threads_init()

        # connect signals for the GUI
        self.connect("destroy", Gtk.main_quit)

        # build up the GUI itself
        self.build_gui()

        # initialize the E+ path, this will be based on the settings last-saved or initial path
        self.refresh_eplus_folder()

        # for good measure, check the validity of the idf/epw versions once at load time
        self.check_file_paths(None)

    def build_gui(self):
        """
        This function manages the window construction, including position, title, and presentation
        """

        # put the window in the center of the (primary? current?) screen
        self.set_position(Gtk.WindowPosition.CENTER)

        # make a nice border around the outside of the window
        self.set_border_width(0)

        # set the window title
        self.set_title(__program_name__)

        # add the body
        self.add(self.gui_build_body())

        # this brings the window to the front (unless the opening terminal is in the way)
        self.present()

        # shows all child widgets recursively
        self.show_all()

    def gui_build_body(self):
        """
        This function builds out the specific widgets on the GUI

        * Returns: A gtk.VBox suitable for adding directly onto the main gtk.Window
        """

        # create a vbox here first
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=self.box_spacing)

        # create the menu bar itself to hold the menus
        mb = Gtk.MenuBar.new()

        # create the actual actionable items under the file menu
        menu_item_file_about = Gtk.MenuItem.new_with_label(_("About..."))
        menu_item_file_about.connect("activate", self.about_dialog)
        menu_item_file_exit = Gtk.MenuItem.new_with_label(_("Exit"))
        menu_item_file_exit.connect("activate", Gtk.main_quit)

        # create the actual actionable items under the language menu
        menu_item_english = Gtk.MenuItem.new_with_label("Language: English")
        menu_item_english.connect("activate", self.switch_language, Languages.English)
        if self.settings[Keys.language] == Languages.English:
            menu_item_english.set_sensitive(False)
        menu_item_spanish = Gtk.MenuItem.new_with_label("Idioma: Espanol")
        menu_item_spanish.connect("activate", self.switch_language, Languages.Spanish)
        if self.settings[Keys.language] == Languages.Spanish:
            menu_item_spanish.set_sensitive(False)

        # create the list of items that will eventually be dropped down, and append items in the right order
        file_menu = Gtk.Menu()
        file_menu.append(menu_item_file_about)
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(menu_item_file_exit)
        language_menu = Gtk.Menu()
        language_menu.append(menu_item_english)
        language_menu.append(menu_item_spanish)

        # create the root drop-down-able menu items, and assign their submenus to the lists above
        menu_item_file = Gtk.MenuItem(_("File"))
        menu_item_file.set_submenu(file_menu)
        menu_item_lang = Gtk.MenuItem("Language/Idioma")
        menu_item_lang.set_submenu(language_menu)

        # attach the root menus to the main menu bar
        mb.append(menu_item_file)
        mb.append(menu_item_lang)

        # and finally attach the main menu bar to the window
        vbox.pack_start(mb, False, False, 0)

        # create the EnergyPlus install button and textbox section
        h_box_0 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.box_spacing)
        button0 = Gtk.Button.new_with_label(_("Choose EnergyPlus Install Folder.."))
        button0.connect("clicked", self.select_eplus_install)
        h_box_0.pack_start(button0, True, True, self.box_spacing)
        self.eplus_install_path = Gtk.Entry()
        self.eplus_install_path.connect("changed", self.check_file_paths)
        self.eplus_install_path.set_text(self.settings[Keys.last_ep_path])
        self.eplus_install_path.set_size_request(width=500, height=-1)
        h_box_0.pack_start(self.eplus_install_path, True, True, self.box_spacing)
        vbox.pack_start(h_box_0, True, True, 0)

        # create the input file button and textbox section
        h_box_1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.box_spacing)
        button1 = Gtk.Button.new_with_label(_("Choose Input File.."))
        button1.connect("clicked", self.select_input_file, FileTypes.IDF)
        h_box_1.pack_start(button1, True, True, self.box_spacing)
        self.input_file_path = Gtk.Entry()
        self.input_file_path.connect("changed", self.check_file_paths)
        self.input_file_path.set_text(self.settings['last_idf'])  # "/tmp/RefBldgHospitalNew2004_Chicago.idf")
        self.input_file_path.set_size_request(width=500, height=-1)
        h_box_1.pack_start(self.input_file_path, True, True, self.box_spacing)
        self.edit_idf_button = Gtk.Button(_("Edit Input File.."))
        self.edit_idf_button.connect("clicked", self.open_input_file)
        h_box_1.pack_start(self.edit_idf_button, True, True, self.box_spacing)
        vbox.pack_start(h_box_1, True, True, 0)

        # create the weather file button and textbox section
        h_box_2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.box_spacing)
        button1 = Gtk.Button(_("Choose Weather File.."))
        button1.connect("clicked", self.select_input_file, FileTypes.EPW)
        h_box_2.pack_start(button1, True, True, self.box_spacing)
        self.weather_file_path = Gtk.Entry()
        self.weather_file_path.connect("changed", self.check_file_paths)
        self.weather_file_path.set_text(
            self.settings['last_epw'])
        self.weather_file_path.set_size_request(width=500, height=-1)
        h_box_2.pack_start(self.weather_file_path, True, True, self.box_spacing)
        vbox.pack_start(h_box_2, True, True, 0)

        # separator
        vbox.pack_start(Gtk.HSeparator(), False, False, 0)

        # create the simulate/cancel button section
        h_box_3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.box_spacing)
        self.button_sim = Gtk.Button(_("Simulate"))
        self.button_sim.connect("clicked", self.run_simulation)
        h_box_3.pack_start(self.button_sim, True, True, self.box_spacing)
        self.button_cancel = Gtk.Button(_("Cancel"))
        self.button_cancel.connect("clicked", self.cancel_simulation)
        self.update_run_buttons(running=False)
        h_box_3.pack_start(self.button_cancel, True, True, self.box_spacing)
        vbox.pack_start(h_box_3, True, True, 0)

        # separator
        vbox.pack_start(Gtk.HSeparator(), False, False, 0)

        # create the status bar
        h_box_4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.box_spacing)
        self.ep_version_label.set_text(_("E+ Version"))
        # noinspection PyTypeChecker
        h_box_4.pack_start(Gtk.VSeparator(), False, False, 0)  # IDE thinks VSeparator is not a Widget, but it is...
        h_box_4.pack_start(self.ep_version_label, False, True, 0)
        self.status_bar = Gtk.Statusbar()
        self.status_bar_context_id = self.status_bar.get_context_id("Statusbar example")
        self.status_bar.push(self.status_bar_context_id, _("Ready for launch"))
        # noinspection PyTypeChecker
        h_box_4.pack_start(Gtk.VSeparator(), False, False, 0)  # IDE thinks VSeparator is not a Widget, but it is...
        # noinspection PyTypeChecker
        h_box_4.pack_start(self.status_bar, False, False, 0)  # IDE thinks StatusBar is not a Widget, but it is...
        vbox.pack_end(h_box_4, False, True, 0)

        # return the vbox
        return vbox

    def open_input_file(self, __):
        tool = 'xdg-open' if system() == 'Linux' else 'open'
        try:
            subprocess.Popen([tool, self.input_file_path.get_text()], shell=False)
        except Exception as e:
            self.simple_error_dialog(
                _("Could not open input file, set default application by opening the file separately first.")
            )
            print(e)

    def switch_language(self, __, language):
        self.settings[Keys.language] = language
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=__program_name__)
        dialog.set_title(_("Message"))
        dialog.format_secondary_text(
            _("You must restart the app to make the language change take effect.  Would you like to restart now?"))
        resp = dialog.run()
        if resp == Gtk.ResponseType.YES:
            self.doing_restart = True
        dialog.destroy()
        if self.doing_restart:
            Gtk.main_quit()

    def refresh_eplus_folder(self):
        self.eplus_path_manager = EnergyPlusPathManager(self.settings[Keys.last_ep_path])
        if self.eplus_path_manager.valid:
            version_string = EnergyPlusThread.get_ep_version(self.eplus_path_manager.executable)
        else:
            version_string = '*Invalid E+ install root folder*'
        self.eplus_install_path.set_text(str(self.eplus_path_manager.eplus_path))
        self.ep_version_label.set_text(version_string)

    def select_eplus_install(self, __):
        dialog = Gtk.FileChooserDialog(
            title=_("Choose EnergyPlus Install Folder"),
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dialog.set_select_multiple(False)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.settings[Keys.last_ep_path] = dialog.get_current_folder()
            self.refresh_eplus_folder()
            dialog.destroy()
        else:
            print(_("Cancelled!"))
            dialog.destroy()

    def select_input_file(self, __, flag):
        message, file_filters = FileTypes.get_materials(flag)
        if flag == FileTypes.IDF:
            key = Keys.last_idf_folder
        else:
            key = Keys.last_epw_folder
        dialog = Gtk.FileChooserDialog(
            title=message,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dialog.set_select_multiple(False)
        for file_filter in file_filters:
            dialog.add_filter(file_filter)
        if self.settings[key] is not None:
            dialog.set_current_folder(self.settings[key])
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.settings[key] = dialog.get_current_folder()
            if flag == FileTypes.IDF:
                self.input_file_path.set_text(dialog.get_filename())
            elif flag == FileTypes.EPW:
                self.weather_file_path.set_text(dialog.get_filename())
            dialog.destroy()
        else:
            print(_("Cancelled!"))
            dialog.destroy()

    def run_simulation(self, __):
        self.running_simulation_thread = EnergyPlusThread(
            self.eplus_path_manager.executable,
            self.input_file_path.get_text(),
            self.weather_file_path.get_text(),
            self.message,
            self.callback_handler_success,
            self.callback_handler_failure,
            self.callback_handler_cancelled
        )
        self.running_simulation_thread.start()
        self.update_run_buttons(running=True)

    def update_run_buttons(self, running=False):
        self.button_sim.set_sensitive(not running)
        self.button_cancel.set_sensitive(running)

    def message(self, message):
        GObject.idle_add(self.message_handler, message)

    def message_handler(self, message):
        self.status_bar.push(self.status_bar_context_id, message)

    def callback_handler_cancelled(self):
        GObject.idle_add(self.cancelled_simulation)

    def cancelled_simulation(self):
        self.update_run_buttons(running=False)

    def callback_handler_failure(self, std_out, run_dir):
        GObject.idle_add(self.failed_simulation, std_out, run_dir)

    def failed_simulation(self, _, run_dir):
        self.update_run_buttons(running=False)
        message = Gtk.MessageDialog(parent=self,
                                    flags=0,
                                    type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.YES_NO,
                                    message_format=_("EnergyPlus Failed!"))
        message.set_title(_("EnergyPlus Failed"))
        message.format_secondary_text(
            _("Error file is the best place to start.  Would you like to open the Run Folder?"))
        response = message.run()
        if response == Gtk.ResponseType.YES:
            subprocess.Popen(['open', run_dir], shell=False)
        message.destroy()

    def callback_handler_success(self, std_out, run_dir):
        GObject.idle_add(self.completed_simulation, std_out, run_dir)

    def completed_simulation(self, std_out, run_dir):
        # update the GUI buttons
        self.update_run_buttons(running=False)
        # create the dialog
        result_dialog = Gtk.Dialog(title=_("Simulation Output"),
                                   transient_for=self,
                                   flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)
        result_dialog.add_buttons(_("Open Run Directory"), Gtk.ResponseType.YES, _("Close"), Gtk.ResponseType.ACCEPT)
        # put a description label
        label = Gtk.Label(_("EnergyPlus Simulation Output:"))
        result_dialog.vbox.pack_start(label, False, True, 0)

        # put the actual simulation results
        std_out_string = std_out.decode('utf-8')
        label = Gtk.Label(std_out_string)
        scrolled_results = Gtk.ScrolledWindow()
        scrolled_results.set_border_width(10)
        scrolled_results.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        scrolled_results.add_with_viewport(label)
        scrolled_results.show()
        result_dialog.vbox.pack_start(scrolled_results, True, True, 0)
        label.show()
        result_dialog.set_size_request(width=500, height=600)
        resp = result_dialog.run()
        if resp == Gtk.ResponseType.YES:
            try:
                if system() == 'Linux':
                    tool = 'xdg-open'
                else:  # assuming Mac
                    tool = 'open'
                subprocess.Popen([tool, run_dir], shell=False)
            except Exception as e:
                self.simple_error_dialog(_("Could not open run directory"))
                print(e)
        result_dialog.destroy()

    def cancel_simulation(self, __):
        self.button_cancel.set_sensitive(False)
        self.running_simulation_thread.stop()

    def check_file_paths(self, __):
        required_pieces = [self.eplus_path_manager, self.weather_file_path, self.input_file_path, self.status_bar]
        if not all(required_pieces):  # they should all be truthy
            return  # we are probably doing early initialization of the GUI
        idf = self.input_file_path.get_text()
        epw = self.weather_file_path.get_text()
        self.settings[Keys.last_idf] = idf
        self.settings[Keys.last_epw] = epw
        if os.path.exists(idf) and os.path.exists(epw) and self.eplus_path_manager.valid:
            self.message_handler(_("Ready for launch"))
            self.button_sim.set_sensitive(True)
            self.edit_idf_button.set_sensitive(True)
        else:
            self.message_handler(_("Input and/or Weather file paths are invalid"))
            self.button_sim.set_sensitive(False)
            self.edit_idf_button.set_sensitive(False)

    def simple_error_dialog(self, message_text):
        message = Gtk.MessageDialog(transient_for=self,
                                    flags=0,
                                    message_type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.OK,
                                    text=_("Error performing prior action:"))
        message.set_title(__program_name__)
        message.format_secondary_text(message_text)
        message.run()
        message.destroy()

    def about_dialog(self, __):
        message = Gtk.MessageDialog(transient_for=self,
                                    flags=0,
                                    message_type=Gtk.MessageType.INFO,
                                    buttons=Gtk.ButtonsType.OK,
                                    text=__program_name__)
        message.set_title(__program_name__)
        message.format_secondary_text(_("ABOUT_DIALOG"))
        message.run()
        message.destroy()

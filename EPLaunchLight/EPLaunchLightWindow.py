import gtk
import json
import os
import gobject
import subprocess

from FileTypes import FileTypes
from EnergyPlusPath import EnergyPlusPath
from EnergyPlusThread import EnergyPlusThread


class EPLaunchLightWindow(gtk.Window):
    """
    This class is the main window class for EP-Luanch-Light
    """

    def __init__(self):
        """
        This initializer function creates instance variables, sets up threading, and builds the GUI
        """

        # initialize the parent class
        super(EPLaunchLightWindow, self).__init__()

        # initialize some class-level "constants"
        self.box_spacing = 4
        self.settings_file_name = os.path.join(os.path.expanduser("~"), ".eplaunchlight.json")

        # initialize instance variables to be set later
        self.input_file_path = None
        self.weather_file_path = None
        self.button_sim = None
        self.button_cancel = None
        self.ep_run_folder = None
        self.running_simulation_thread = None
        self.status_bar = None
        self.status_bar_context_id = None
        self.ep_version_label = None

        # try to load the settings
        # TODO: Persist this in a config file, along with history of files run
        self.settings = None
        self.load_settings()

        # prepare threading
        gobject.threads_init()

        # connect signals for the GUI
        self.connect("destroy", self.quit)

        # build up the GUI itself
        self.build_gui()

        # update the list of E+ versions
        self.ep_run_folder = EnergyPlusPath.get_latest_eplus_version()
        just_version_number = EnergyPlusPath.get_version_number_from_path(self.ep_run_folder)
        self.ep_version_label.set_text(EnergyPlusPath.get_descriptor_from_version_number(just_version_number))

        # for good measure, check the validity of the idf/epw versions once at load time
        self.check_file_paths(None)

    def load_settings(self):
        try:
            self.settings = json.load(open(self.settings_file_name))
        except Exception:
            self.settings = {}
        if 'last_folder_path' not in self.settings:
            self.settings['last_folder_path'] = os.path.expanduser("~")
        if 'last_idf' not in self.settings:
            self.settings['last_idf'] = '/path/to/idf'
        if 'last_epw' not in self.settings:
            self.settings['last_epw'] = '/path/to/epw'

    def save_settings(self):
        try:
            json.dump(self.settings, open(self.settings_file_name,'w'))
        except Exception:
            pass

    def quit(self, widget=None):
        try:
            self.save_settings()
        except Exception:
            pass
        gtk.main_quit()

    def build_gui(self):
        """
        This function manages the window construction, including position, title, and presentation
        """

        # put the window in the center of the (primary? current?) screen
        self.set_position(gtk.WIN_POS_CENTER)

        # make a nice border around the outside of the window
        self.set_border_width(0)

        # set the window title
        self.set_title("EnergyPlus Launch Light")

        # add the body
        self.add(self.gui_build_body())

        # this brings the window to the front (unless the opening terminal is in the way)
        self.present()

        # shows all child widgets recursively
        self.show_all()

    def framed(self, thing, color_code="#DB5700"):
        frames_on = False
        if not frames_on:
            return thing
        f = gtk.Frame()
        f.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(color_code))
        f.add(thing)
        return f

    def gui_build_body(self):
        """
        This function builds out the specific widgets on the GUI

        * Returns: A gtk.VBox suitable for adding directly onto the main gtk.Window
        """

        # create a vbox here first
        vbox = gtk.VBox(False, self.box_spacing)

        # separator
        vbox.pack_start(gtk.HSeparator(), False)

        # create the input file button and textbox section
        hbox1 = gtk.HBox(False, self.box_spacing)
        button1 = gtk.Button("Choose Input File..")
        button1.connect("clicked", self.select_input_file, FileTypes.IDF)
        alignment = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=0.5)
        alignment.add(button1)
        hbox1.pack_start(alignment, True, True, self.box_spacing)
        self.input_file_path = gtk.Entry()
        self.input_file_path.connect("changed", self.check_file_paths)
        self.input_file_path.set_text(self.settings['last_idf'])  # "/tmp/RefBldgHospitalNew2004_Chicago.idf")
        self.input_file_path.set_size_request(width=500, height=-1)
        alignment = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=0.5)
        alignment.add(self.input_file_path)
        hbox1.pack_start(alignment, True, True, self.box_spacing)
        vbox.pack_start(self.framed(hbox1), True, True, 0)

        # create the weather file button and textbox section
        hbox2 = gtk.HBox(False, self.box_spacing)
        button1 = gtk.Button("Choose Weather File..")
        button1.connect("clicked", self.select_input_file, FileTypes.EPW)
        alignment = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=0.5)
        alignment.add(button1)
        hbox2.pack_start(alignment, True, True, self.box_spacing)
        self.weather_file_path = gtk.Entry()
        self.weather_file_path.connect("changed", self.check_file_paths)
        self.weather_file_path.set_text(self.settings['last_epw'])  # '"/Users/elee/EnergyPlus/repos/2eplus/weather/CZ06RV2.epw")
        self.weather_file_path.set_size_request(width=500, height=-1)
        alignment = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=0.5)
        alignment.add(self.weather_file_path)
        hbox2.pack_start(alignment, True, True, self.box_spacing)
        vbox.pack_start(self.framed(hbox2), True, True, 0)

        # separator
        vbox.pack_start(self.framed(gtk.HSeparator()), False)

        # create the simulate/cancel button section
        hbox3 = gtk.HBox(False, self.box_spacing)
        self.button_sim = gtk.Button("Simulate")
        self.button_sim.connect("clicked", self.run_simulation)
        alignment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.5)
        alignment.add(self.button_sim)
        hbox3.pack_start(alignment, True, True, self.box_spacing)
        self.button_cancel = gtk.Button("Cancel")
        self.button_cancel.connect("clicked", self.cancel_simulation)
        alignment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.5)
        alignment.add(self.button_cancel)
        self.update_run_buttons(running=False)
        hbox3.pack_start(alignment, True, True, self.box_spacing)
        vbox.pack_start(self.framed(hbox3), True, True, 0)

        # separator
        vbox.pack_start(self.framed(gtk.HSeparator()), False)

        # create the status bar
        hbox = gtk.HBox(False, self.box_spacing)
        self.ep_version_label = gtk.Label()
        self.ep_version_label.set_text("E+ Version")
        aligner = gtk.Alignment(1, 1, 1, 1)
        aligner.add(self.ep_version_label)
        hbox.pack_start(self.framed(gtk.VSeparator()), False)
        hbox.pack_start(aligner, False, True, 0)
        self.status_bar = gtk.Statusbar()
        self.status_bar.set_has_resize_grip(False)
        self.status_bar_context_id = self.status_bar.get_context_id("Statusbar example")
        self.status_bar.push(self.status_bar_context_id, "Ready for launch")
        aligner = gtk.Alignment(1, 1, 1, 0)
        aligner.add(self.status_bar)
        hbox.pack_start(self.framed(gtk.VSeparator()), False)
        hbox.pack_start(aligner)
        vbox.pack_end(self.framed(hbox), False, True, 0)
        hbox.pack_start(self.framed(gtk.VSeparator()), False)

        # return the vbox
        return vbox

    def select_input_file(self, widget, flag):
        message, file_filters = FileTypes.get_materials(flag)
        dialog = gtk.FileChooserDialog(
            title=message,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        )
        dialog.set_select_multiple(False)
        for file_filter in file_filters:
            dialog.add_filter(file_filter)
        if self.settings['last_folder_path'] is not None:
            dialog.set_current_folder(self.settings['last_folder_path'])
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.settings['last_folder_path'] = dialog.get_current_folder()
            if flag == FileTypes.IDF:
                self.input_file_path.set_text(dialog.get_filename())
            elif flag == FileTypes.EPW:
                self.weather_file_path.set_text(dialog.get_filename())
            dialog.destroy()
        else:
            print("Cancelled!")
            dialog.destroy()

    def run_simulation(self, widget):
        self.running_simulation_thread = EnergyPlusThread(
            os.path.join(self.ep_run_folder, 'EnergyPlus'),
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
        gobject.idle_add(self.message_handler, message)

    def message_handler(self, message):
        self.status_bar.push(self.status_bar_context_id, message)

    def callback_handler_cancelled(self):
        gobject.idle_add(self.cancelled_simulation)

    def cancelled_simulation(self):
        self.update_run_buttons(running=False)

    def callback_handler_failure(self, std_out, run_dir):
        gobject.idle_add(self.failed_simulation, std_out, run_dir)

    def failed_simulation(self, std_out, run_dir):
        self.update_run_buttons(running=False)
        message = gtk.MessageDialog(parent=self,
                                    flags=0,
                                    type=gtk.MESSAGE_ERROR,
                                    buttons=gtk.BUTTONS_YES_NO,
                                    message_format="EnergyPlus Failed!")
        message.set_title("EnergyPlus Failed")
        message.format_secondary_text("Error file is the best place to start.  Would you like to open the Run Folder?")
        response = message.run()
        if response ==  gtk.RESPONSE_YES:
            subprocess.Popen(['open', run_dir], shell=False)
        message.destroy()

    def callback_handler_success(self, std_out, run_dir):
        gobject.idle_add(self.completed_simulation, std_out, run_dir)

    def completed_simulation(self, std_out, run_dir):
        # update the GUI buttons
        self.update_run_buttons(running=False)
        # create the dialog
        result_dialog = gtk.Dialog("Simulation Output",
                                   self,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   ("Open Run Directory", gtk.RESPONSE_YES, gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT)
                                   )
        # put a description label
        label = gtk.Label("EnergyPlus Simulation Output:")
        label.show()
        aligner = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=1.0)
        aligner.add(label)
        aligner.show()
        result_dialog.vbox.pack_start(aligner, False, True, 0)

        # put the actual simulation results
        label = gtk.Label(std_out)
        scrolled_results = gtk.ScrolledWindow()
        scrolled_results.set_border_width(10)
        scrolled_results.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scrolled_results.add_with_viewport(label)
        scrolled_results.show()
        result_dialog.vbox.pack_start(scrolled_results, True, True, 0)
        label.show()
        result_dialog.set_size_request(width=500, height=600)
        resp = result_dialog.run()
        if resp == gtk.RESPONSE_YES:
            subprocess.Popen(['open', run_dir], shell=False)
        result_dialog.destroy()

    def cancel_simulation(self, widget):
        self.button_cancel.set_sensitive(False)
        self.running_simulation_thread.stop()

    def check_file_paths(self, widget):
        if self.weather_file_path is None or self.input_file_path is None or self.status_bar is None:
            return  # we are probably doing early initialization of the GUI
        idf = self.input_file_path.get_text()
        epw = self.weather_file_path.get_text()
        self.settings['last_idf'] = idf
        self.settings['last_epw'] = epw
        if os.path.exists(idf) and os.path.exists(epw):
            self.message_handler("Ready for launch")
            self.button_sim.set_sensitive(True)
        else:
            self.message_handler("Input and/or Weather file paths are invalid")
            self.button_sim.set_sensitive(False)



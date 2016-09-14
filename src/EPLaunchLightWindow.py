import gtk
import os
import gobject

from FileTypes import FileTypes
from EnergyPlusPath import EnergyPlusPath
from EnergyPlusThread import EnergyPlusThread


class EPLaunchLightWindow(gtk.Window):

    def __init__(self):

        # initialize the parent class
        super(EPLaunchLightWindow, self).__init__()

        # initialize some class-level "constants"
        self.box_spacing = 10

        # initialize instance variables to be set later
        self.input_file_path = None
        self.weather_file_path = None
        self.button_sim = None
        self.button_cancel = None
        self.ep_run_folder = None
        self.running_simulation_thread = None
        self.status_bar = None
        self.status_bar_context_id = None

        # prepare threading
        gobject.threads_init()

        # connect signals for the GUI
        self.connect("destroy", gtk.main_quit)

        # build up the GUI itself
        self.build_gui()

        # update the list of E+ versions
        self.ep_run_folder = EnergyPlusPath.get_latest_eplus_version()

    def build_gui(self):

        # put the window in the center of the (primary? current?) screen
        self.set_position(gtk.WIN_POS_CENTER)

        # make a nice border around the outside of the window
        self.set_border_width(0)

        # set the window title
        self.set_title("EnergyPlus Launch Light")

        # set the background color
        # self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#DB5700"))

        # add the body
        self.add(self.gui_build_body())

        # this brings the window to the front (unless the opening terminal is in the way)
        self.present()

        # shows all child widgets recursively
        self.show_all()

    def gui_build_body(self):

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
        self.input_file_path.set_text("/tmp/RefBldgHospitalNew2004_Chicago.idf")
        self.input_file_path.set_size_request(width=500, height=-1)
        alignment = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=0.5)
        alignment.add(self.input_file_path)
        hbox1.pack_start(alignment, True, True, self.box_spacing)
        vbox.pack_start(hbox1, True, True, 0)

        # create the weather file button and textbox section
        hbox2 = gtk.HBox(False, self.box_spacing)
        button1 = gtk.Button("Choose Weather File..")
        button1.connect("clicked", self.select_input_file, FileTypes.EPW)
        alignment = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=0.5)
        alignment.add(button1)
        hbox2.pack_start(alignment, True, True, self.box_spacing)
        self.weather_file_path = gtk.Entry()
        self.weather_file_path.connect("changed", self.check_file_paths)
        self.weather_file_path.set_text("/Users/elee/EnergyPlus/repos/2eplus/weather/CZ06RV2.epw")
        self.weather_file_path.set_size_request(width=500, height=-1)
        alignment = gtk.Alignment(xalign=1.0, yalign=0.5, xscale=1.0, yscale=0.5)
        alignment.add(self.weather_file_path)
        hbox2.pack_start(alignment, True, True, self.box_spacing)
        vbox.pack_start(hbox2, True, True, 0)

        # separator
        vbox.pack_start(gtk.HSeparator(), False)

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
        vbox.pack_start(hbox3, True, True, 0)

        # separator
        vbox.pack_start(gtk.HSeparator(), False)

        # create the status bar
        self.status_bar = gtk.Statusbar()
        self.status_bar.set_has_resize_grip(False)
        self.status_bar_context_id = self.status_bar.get_context_id("Statusbar example")
        self.status_bar.push(self.status_bar_context_id, "Ready for launch")
        aligner = gtk.Alignment(1, 1, 1, 0)
        aligner.add(self.status_bar)
        vbox.pack_end(aligner, False, True, 0)

        # return the vbox
        return vbox

    def select_input_file(self, widget, flag):
        message, pattern_message, pattern = FileTypes.get_materials(flag)
        dialog = gtk.FileChooserDialog(
            title=message,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        )
        dialog.set_select_multiple(False)
        file_filter = gtk.FileFilter()
        file_filter.set_name(pattern_message)
        file_filter.add_pattern(pattern)
        dialog.add_filter(file_filter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
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
            os.path.join(self.ep_run_folder, 'runenergyplus'),
            self.input_file_path.get_text(),
            self.weather_file_path.get_text(),
            self.message,
            self.completed_simulation
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

    def completed_simulation(self, std_out):
        gobject.idle_add(self.completed_simulation_handler, std_out)

    def completed_simulation_handler(self, std_out):
        self.update_run_buttons(running=False)
        label = gtk.Label('\n' + std_out)
        # label.set_line_wrap(True)
        result_dialog = gtk.Dialog("Simulation Output",
                                   self,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
                                   )
        scrolled_results = gtk.ScrolledWindow()
        scrolled_results.set_border_width(10)
        scrolled_results.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scrolled_results.add_with_viewport(label)
        scrolled_results.show()
        result_dialog.vbox.pack_start(scrolled_results, True, True, 0)
        label.show()
        result_dialog.set_size_request(width=400,height=600)
        result_dialog.run()
        result_dialog.destroy()
        # label = gtk.Label(std_out)
        # label.set_line_wrap(True)
        # scrolled_results.add_with_viewport(label)
        # result_dialog.show()

    def cancel_simulation(self, widget):
        self.running_simulation_thread.stop()

    def check_file_paths(self, widget):
        if self.weather_file_path is None or self.input_file_path is None or self.status_bar is None:
            return  # we are probably doing early initialization of the GUI
        idf = self.input_file_path.get_text()
        epw = self.weather_file_path.get_text()
        if os.path.exists(idf) and os.path.exists(epw):
            self.message_handler("Ready for launch")
            self.button_sim.set_sensitive(True)
        else:
            self.message_handler("Input and/or Weather file paths are invalid")
            self.button_sim.set_sensitive(False)



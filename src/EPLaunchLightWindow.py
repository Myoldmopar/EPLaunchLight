import gtk
import glob

from helpers import FileTypes, EnergyPlusPath


class EPLaunchLightWindow(gtk.Window):

    box_spacing = 2

    def __init__(self):

        # initialize the parent class
        super(EPLaunchLightWindow, self).__init__()

        # connect signals for the GUI
        self.connect("destroy", self.go_away)

        # build up the GUI itself
        self.build_gui()

        # update the list of E+ versions
        self.update_ep_versions()

    def go_away(self, what_else_goes_in_gtk_main_quit):

        # just call the gtk standard exit method
        gtk.main_quit()

    def build_gui(self):

        # put the window in the center of the (primary? current?) screen
        self.set_position(gtk.WIN_POS_CENTER)

        # make a nice border around the outside of the window
        self.set_border_width(10)

        # set the window title
        self.set_title("EnergyPlus Launch Light")

        # add the body
        self.add(self.gui_build_body())

        # this brings the window to the front (unless the opening terminal is in the way)
        self.present()

        # shows all child widgets recursively
        self.show_all()

    def update_ep_versions(self):

        # get all the installed versions first, sorted
        install_folders = glob.glob('/Applications/EnergyPlus*')
        versions = sorted([EnergyPlusPath.get_version_number_from_path(x) for x in install_folders])
        print("Available versions:")
        print(versions)

    def gui_build_body(self):

        # create a vbox here first
        vbox = gtk.VBox(False, self.box_spacing)

        # create the input file button and textbox section
        hbox1 = gtk.HBox(False, self.box_spacing)
        button1 = gtk.Button("Choose Input File..")
        button1.connect("clicked", self.select_input_file, FileTypes.IDF)
        hbox1.pack_start(button1, False, False, self.box_spacing)
        self.input_file_path = gtk.Entry()
        hbox1.pack_start(self.input_file_path, True, True, self.box_spacing)
        vbox.pack_start(hbox1)

        # create the weather file button and textbox section
        hbox2 = gtk.HBox(False, self.box_spacing)
        button1 = gtk.Button("Choose Weather File..")
        button1.connect("clicked", self.select_input_file, FileTypes.EPW)
        hbox2.pack_start(button1, False, False, self.box_spacing)
        self.weather_file_path = gtk.Entry()
        hbox2.pack_start(self.weather_file_path, True, True, self.box_spacing)
        vbox.pack_start(hbox2)

        # create the simulate/cancel button section
        hbox3 = gtk.HBox(False, self.box_spacing)
        button_settings = gtk.Button("Settings")
        button_settings.connect("clicked", self.update_settings)
        alignment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.0)
        alignment.add(button_settings)
        hbox3.pack_start(alignment, False, False, self.box_spacing)
        self.button_sim = gtk.Button("Simulate")
        self.button_sim.connect("clicked", self.run_simulation)
        alignment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.0)
        alignment.add(self.button_sim)
        hbox3.pack_start(alignment, False, False, self.box_spacing)
        self.button_cancel = gtk.Button("Cancel")
        self.button_cancel.connect("clicked", self.cancel_simulation)
        alignment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.0)
        alignment.add(self.button_cancel)
        hbox3.pack_start(alignment, False, False, self.box_spacing)
        vbox.pack_start(hbox3)

        # return the vbox
        return vbox

    def select_input_file(self, widget, flag):
        message, pattern_message, pattern = FileTypes.get_materials(flag)
        dialog = gtk.FileChooserDialog(title=message, action = gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_select_multiple(False)
        #if self.last_folder_path != None:
        #    dialog.set_current_folder(self.last_folder_path)
        afilter = gtk.FileFilter()
        afilter.set_name(pattern_message)
        afilter.add_pattern(pattern)
        dialog.add_filter(afilter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            #self.last_folder_path = dialog.get_current_folder()
            print("Success! %s" % dialog.get_filename())
            #self.runtime_report_file = dialog.get_filename()
            #self.suite_option_runtime_file_label.set_label(self.runtime_report_file)
            dialog.destroy()
        else:
            print("Cancelled!")
            dialog.destroy()
            # reset the flag
            return

    def run_simulation(self, widget):
        print(widget)

    def cancel_simulation(self, widget):
        print(widget)

    def update_settings(self, widget):
        print(widget)

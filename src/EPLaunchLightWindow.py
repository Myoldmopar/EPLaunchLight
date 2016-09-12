import gtk

class EPLaunchLightWindow(gtk.Window):

    def __init__(self):

        # initialize the parent class
        super(EPLaunchLightWindow, self).__init__()

        # connect signals for the GUI
        self.connect("destroy", self.go_away)

        # build up the GUI itself
        self.build_gui()

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

		# create a vbox to start laying out the geometry of the form
		vbox = gtk.VBox(False, 3)

		# now add the entire vbox to the main form
		self.add(vbox)

		# shows all child widgets recursively
		self.show_all()

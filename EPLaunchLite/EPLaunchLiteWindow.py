import os
from platform import system
import subprocess
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import tkinter.scrolledtext as st
from queue import Queue

from EPLaunchLite import VERSION
from EPLaunchLite.EnergyPlusPath import EnergyPlusPathManager
from EPLaunchLite.EnergyPlusThread import EnergyPlusThread
from EPLaunchLite.FileTypes import FileTypes
from EPLaunchLite.Settings import Keys


class Window:
    """
    This class is the main window class for EP-Launch-Lite
    """

    def __init__(self, settings):
        """
        This initializer function creates instance variables, sets up threading, and builds the GUI
        """

        self.root = tk.Tk()
        self.root.title(f"EP-Launch-Lite (v{VERSION})")

        # initialize some class-level "constants"
        self.box_spacing = 4

        # initialize instance variables to be set later
        self.input_file_path = None
        self.weather_file_path = None
        self.button_sim = None
        self.ep_run_folder = None
        self.running_simulation_thread = None
        self.eplus_path_manager = None

        # try to load the settings very early since it includes initialization
        self.settings = settings

        # build up the GUI itself
        self._gui_build_body()

        # initialize the E+ path, this will be based on the settings last-saved or initial path
        self.refresh_eplus_folder()

        # for good measure, check the validity of the idf/epw versions once at load time
        self.check_file_paths()

        # set up the gui worker queue for tracking background thread requests
        self.gui_queue = Queue()
        self.check_queue()

    def check_queue(self):
        while True:
            # noinspection PyBroadException
            try:
                task = self.gui_queue.get(block=False)
                self.root.after_idle(task)
            except Exception:
                break
        self.root.after(100, self.check_queue)

    def _gui_build_body(self):

        # create the EnergyPlus install button and textbox section
        eplus_install_button = tk.Button(
            self.root, text="Choose EnergyPlus Install Folder..", command=self.select_eplus_install
        )
        eplus_install_button.grid(column=0, row=0, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing)
        self.eplus_install_path = tk.StringVar(self.root, self.settings[Keys.last_ep_path])
        self.eplus_install_path_label = tk.Label(self.root, textvariable=self.eplus_install_path)
        self.eplus_install_path_label.grid(
            column=1, row=0, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing
        )

        # create the input file button and textbox section
        button1 = tk.Button(
            self.root, text="Choose Input File..", command=lambda: self.select_input_file(FileTypes.IDF)
        )
        button1.grid(column=0, row=1, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing)
        self.input_file_path = tk.StringVar(self.root, self.settings['last_idf'])
        self.input_file_path_label = tk.Label(self.root, textvariable=self.input_file_path)
        self.input_file_path_label.grid(
            column=1, row=1, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing
        )
        edit_idf_button = tk.Button(self.root, text="Edit Input File..", command=self.open_input_file)
        edit_idf_button.grid(column=2, row=1, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing)

        # create the weather file button and textbox section
        button1 = tk.Button(
            self.root, text="Choose Weather File..", command=lambda: self.select_input_file(FileTypes.EPW)
        )
        button1.grid(column=0, row=2, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing)
        self.weather_file_path = tk.StringVar(self.root, self.settings['last_epw'])
        self.weather_file_path_label = tk.Label(self.root, textvariable=self.weather_file_path)
        self.weather_file_path_label.grid(column=1, row=2, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing)

        # create the simulate/cancel button section
        self.button_sim = tk.Button(self.root, text="Simulate", command=self.run_simulation)
        self.button_sim.grid(column=0, row=3, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing)
        self.update_run_buttons(running=False)

        # # create the status bar
        self.status_bar_var = tk.StringVar(self.root, "Status updates here")
        self.status_bar = tk.Label(self.root, textvariable=self.status_bar_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(
            column=0, columnspan=3, row=4, sticky=tk.NSEW, padx=self.box_spacing, pady=self.box_spacing
        )

    def open_input_file(self):
        tool = 'xdg-open' if system() == 'Linux' else 'open'
        try:
            subprocess.Popen([tool, self.input_file_path.get_text()], shell=False)
        except Exception as e:
            mb.showerror(
                title="Error",
                message="Could not open input file, set default application by opening the file separately first."
            )
            print(e)

    def refresh_eplus_folder(self):
        self.eplus_path_manager = EnergyPlusPathManager(self.settings[Keys.last_ep_path])
        if self.eplus_path_manager.valid:
            version_string = EnergyPlusThread.get_ep_version(self.eplus_path_manager.executable)
        else:
            version_string = '*Invalid E+ install root folder*'
        self.eplus_install_path.set(str(self.eplus_path_manager.eplus_path))
        self.status_bar_var.set(version_string)

    def select_eplus_install(self):
        response = fd.askdirectory(title="Choose EnergyPlus Install Folder")
        if response:
            self.settings[Keys.last_ep_path] = response
            self.refresh_eplus_folder()

    def select_input_file(self, flag):
        message, file_filters = FileTypes.get_materials(flag)
        if flag == FileTypes.IDF:
            key = Keys.last_idf_folder
        else:
            key = Keys.last_epw_folder
        if self.settings[key] is not None:
            response = fd.askopenfilename(title=message, filetypes=file_filters, initialdir=self.settings[key])
        else:
            response = fd.askopenfilename(title=message, filetypes=file_filters)
        if response:
            self.settings[key] = os.path.dirname(response)
            if flag == FileTypes.IDF:
                self.settings[Keys.last_idf] = response
                self.input_file_path.set(response)
            elif flag == FileTypes.EPW:
                self.settings[Keys.last_epw] = response
                self.weather_file_path.set(response)

    def run_simulation(self):
        self.running_simulation_thread = EnergyPlusThread(
            self.eplus_path_manager.executable,
            self.input_file_path.get(),
            self.weather_file_path.get(),
            self.message,
            self.callback_handler_success,
            self.callback_handler_failure,
            self.callback_handler_cancelled
        )
        self.running_simulation_thread.start()
        self.update_run_buttons(running=True)

    def update_run_buttons(self, running=False):
        self.button_sim["state"] = "normal" if not running else "disabled"
        # self.button_cancel["state"] = "normal" if running else "disabled"

    def message(self, message):
        self.gui_queue.put(lambda: self.message_handler(message))

    def message_handler(self, message):
        self.status_bar_var.set(message)

    def callback_handler_cancelled(self):
        self.gui_queue.put(self.cancelled_simulation)

    def cancelled_simulation(self):
        self.update_run_buttons(running=False)

    def callback_handler_failure(self, std_out):
        self.gui_queue.put(lambda: self.failed_simulation(std_out))

    def failed_simulation(self, std_out):
        self.update_run_buttons(running=False)
        mb.showerror(title="EnergyPlus Failed", message=f"EnergyPlus Failed! Standard Output: \n{std_out}")

    def callback_handler_success(self, std_out):
        self.gui_queue.put(lambda: self.completed_simulation(std_out))

    def completed_simulation(self, std_out):
        # update the GUI buttons
        self.update_run_buttons(running=False)
        # create the dialog
        popup = tk.Toplevel(master=self.root)
        popup.title("Simulation Completed")
        text_area = st.ScrolledText(popup, font=("Courier", 12))
        text_area.grid(column=0, sticky=tk.NSEW, pady=10, padx=10)
        text_area.insert(tk.INSERT, std_out)
        text_area.configure(state='disabled')
        popup.mainloop()

    def check_file_paths(self):
        required_pieces = [self.eplus_path_manager, self.weather_file_path, self.input_file_path]  # , self.status_bar]
        if not all(required_pieces):  # they should all be truthy
            return  # we are probably doing early initialization of the GUI
        idf = self.input_file_path.get()
        epw = self.weather_file_path.get()
        self.settings[Keys.last_idf] = idf
        self.settings[Keys.last_epw] = epw
        if os.path.exists(idf) and os.path.exists(epw) and self.eplus_path_manager.valid:
            # self.message_handler("Ready for launch")
            self.button_sim["state"] = "normal"
            # self.edit_idf_button["state"] = "normal"
        else:
            # self.message_handler("Input and/or Weather file paths are invalid")
            self.button_sim["state"] = "disabled"
            # self.edit_idf_button["state"] = "disabled"

import threading
import subprocess


class EnergyPlusThread(threading.Thread):

    def __init__(self, run_script, input_file, weather_file, msg_callback, done_callback):
        self.std_out = None
        self.std_err = None
        self.run_script = run_script
        self.input_file = input_file
        self.weather_file = weather_file
        self.msg_callback = msg_callback
        self.done_callback = done_callback
        threading.Thread.__init__(self)

    def run(self):
        self.msg_callback("Preparing to run")
        p = subprocess.Popen([self.run_script, self.input_file, self.weather_file],
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        self.msg_callback("Subprocess instantiated")
        self.std_out, self.std_err = p.communicate()
        self.msg_callback("Subprocess completed")
        self.done_callback(self.std_out)

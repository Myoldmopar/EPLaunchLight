import threading
import subprocess
import os


class EnergyPlusThread(threading.Thread):
    def __init__(self, run_script, input_file, weather_file, msg_callback, done_callback):
        self.p = None
        self.std_out = None
        self.std_err = None
        self.run_script = run_script
        self.input_file = input_file
        self.weather_file = weather_file
        self.msg_callback = msg_callback
        self.done_callback = done_callback
        threading.Thread.__init__(self)

    def run(self):
        self.p = subprocess.Popen([self.run_script, self.input_file, self.weather_file],
                                  shell=False,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        self.msg_callback("Simulation started")
        self.std_out, self.std_err = self.p.communicate()
        if self.p.returncode == 0:
            self.msg_callback("Simulation completed")
        else:
            self.msg_callback("Simulation failed or was cancelled")
        self.done_callback(self.std_out)

    def stop(self):
        if self.p.poll() is None:
            self.msg_callback("Attempting to cancel simulation ...")
            os.system('pkill -TERM -P {pid}'.format(pid=self.p.pid))

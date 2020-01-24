#LyfeOnEdge 2019
#GPL3
import os
import sys
import subprocess
import threading

class asyncThread(threading.Thread):
	def __init__(self, func, arglist):
		threading.Thread.__init__(self, target=func, args=arglist)
		self.handled = False
		self.arglist = arglist

	def begin(self):
		self.start()

class runnerThread(asyncThread):
	def __init__(self, script_path, arglist):
		self.script_path = script_path
		self.args = arglist
		super().__init__(lambda: self.keepalive(script_path), arglist)

	def keepalive(self, script_path):
		p = subprocess.Popen([sys.executable, '-u', script_path],
				stdout=subprocess.PIPE, 
				stderr=subprocess.STDOUT, 
				bufsize=1,
		)
		with p.stdout:
			for line in iter(p.stdout.readline, b''):
				print(line)
		p.wait()

class asyncThreader():
	def __init__(self):
		self.running_threads = []
		self.update_running_threads()

	def do_continously(self, script_path, arglist = []):
		t = runnerThread(script_path, arglist)
		t.begin()
		self.running_threads.append(t)

	#Not to be called by user
	def update_running_threads(self):
		if self.running_threads:
			for t in self.running_threads:
				if not t.isAlive():
					self.do_continously(t.script_path, t.args)
			self.running_threads = [t for t in self.running_threads if not t.handled]

		self.watchdog = threading.Timer(0.05, self.update_running_threads)
		self.watchdog.start()

threader = asyncThreader()

with open("scripts.txt") as scripts:
	for script in scripts:
		threader.do_continously(os.path.abspath(script), [])

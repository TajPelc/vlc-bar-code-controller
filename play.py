import os
import time
import re
import json
import telnetlib
import threading
from threading import Timer
import subprocess
import pythoncom
import pyHook

newline = "\n"
pattern = re.compile("^[A-Z,0-9]{1}$")
video_id = []
videos = {
    3830037944247: {
        "id": 5,
        "filename": "1.mpg",
        "duration": 55
    },
    6420900002067: {
        "id": 4,
        "filename" : "2.mp4",
        "duration": 120
    },
    9006380122401: {
        "id": 7,
        "filename": "3.mp4",
        "duration": 41
    },
    3838531033870: {
        "id": 6,
        "filename": "4.wmv",
        "duration": 30
    }
}

class Intro(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def run(self):
        while not self.event.is_set():
            print 'Play intro'
            if player.connected:
                player.changeFile(3830037944247)
                self.event.wait(5)

    def stop(self):
        self.event.set()

# VLC class
class VLC(threading.Thread):
    server = '127.0.0.1'
    port = '4212'
    password = 'kekbur'
    connected = False
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        print 'Running VLC player'
        p = subprocess.Popen(['vlc', '-f', '-I', 'telnet', '--telnet-password', self.password],
            shell=False,
            stdout=False,
            stderr=False)
    def log_in(self):
        time.sleep(2)
        self.connection = telnetlib.Telnet(self.server, self.port)
        self.connection.read_until("Password: ")
        self.connection.write(self.password + newline)
    def connect(self):
        if not self.connected:
            try:
                self.start()
                self.join()
                self.log_in()
                self.addFiles()
                self.connected = True
            except IOError:
                exit(1)
    def cmd(self, input):
        self.connection.read_until("> ")
        self.connection.write(input + newline)
    def changeFile(self, id):
        if id != 3830037944247:
            print 'Changing to video %s (%s seconds)' % (videos[id]['filename'], str(videos[id]['duration']))
            self.intro.stop()
            try:
                print type(self.introTimer)
                if self.introTimer:
                    print 'Timer canceled'
                    self.introTimer.cancel()
            except AttributeError:
                pass
            self.introTimer = Timer(videos[id]['duration'], self.playIntro)
            self.introTimer.start()
        self.playing = id
        self.cmd("goto " + str(videos[id]['id']))
        self.cmd("F on")
    def shutdown(self):
        self.connected = False
        self.cmd("shutdown")
        self.connection.close()
        exit(0)
    def addFiles(self):
        for id, clip in videos.items():
            self.cmd("add " + os.path.realpath(clip['filename']))
            print "add " + os.path.realpath(clip['filename'])
        self.cmd("sort title")
    def playIntro(self):
        self.intro = Intro()
        self.intro.start()

# catch keyboard events
player = VLC()
player.connect()
player.playIntro()


def OnKeyboardEvent(event):
    global video_id

    if event.Key == 'Escape':
        player.shutdown()

    # on return play video
    if event.Key == 'Return':
        try:
            id = int(''.join(video_id))
            video_id = []
            if id in videos:
                print id
                player.changeFile(id)
        except ValueError:
            print 'Invalid ID'
        return True # intercept key event

    # for alphanumeric keys, build the key
    if pattern.match(event.Key) is not None:
        video_id.append(event.Key)
        return True # intercept key event

    # do not return to other handlers
    return True

# create a hook manager
hm = pyHook.HookManager()

# watch for all mouse events

hm.KeyDown = OnKeyboardEvent

# set the hook
hm.HookKeyboard()

# wait forever
pythoncom.PumpMessages()
#!/bin/env python

# import required libraries
try:
    import sys
    import subprocess
    import os
    import time
    import re
    import json
    import pyadb
    import uiautomator
    import misc
    import fcntl
    import signal
    import uuid

    from pprint import pprint as pp

except ImportError, error:
    print("Error: missing library [ %s ]" % error.args[0])
    sys.exit(-1)


# class built around uiautomator and adb
class testDevice:

    # initialization: checking adb path, restarting adb,
    # and setting a proper device
    def __init__(self, gui):

        self.config = None
        self.adb = None
        self.devices = None
        self.status = None
        self.uad = None
        self.ui = gui
        self.__file = None
        self.sequence = []
        self.sequence_replay = []

        self.menu_button = [(1,229,1),(0,0,0),(1,229,0),(0,0,0)]
        self.back_button = [(1,158,1),(0,0,0),(1,158,0),(0,0,0)]

        self.ui.sprint("Load config file and adb")
        main_config = json.load(open("./main.json"))
        app_config = json.load(open(self.ui.test_config))
        self.config = misc.json_merge(main_config, app_config)
        self.adb = pyadb.ADB(self.config['adb'])

        self.app_name = self.ui.test_config.replace('conf/','').replace('.json','')

        self.ui.sprint("Verify that adb is in path")
        if not self.adb.check_path():
            raise ValueError("adb is not found, check your path")

        self.ui.sprint("check if aapt exists and is executable")
        if not (os.path.isfile(self.config['aapt'])
                and os.access(self.config['aapt'], os.X_OK)):
            raise ValueError("appt is not found, check your path")

        self.ui.sprint("Check if apk file exists")
        if not os.path.isfile(self.config['app']):
            raise ValueError("unable to open " + self.config['app'])

        self.ui.sprint("Get apk information using aapt")

        # aapt parameters are hardcored at the moment
        p = subprocess.Popen([self.config['aapt'], 'dump', 'badging',
                              self.config['app']], bufsize=-1,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.ui.sprint("Retrieve app package name and its default activity")
        # parameters to look for are hardcoded at the moment
        for l in iter(p.stdout.readline, ''):
            if 'package: name' in l:
                self.config['app.name'] = re.search('name=.([^\'\"]+).',
                                                    l.strip()).group(1)
            elif 'launchable-activity: name' in l and self.config['app.name'] in l:
                self.config['app.activity'] = re.search('name=.([^\'\"]+).',
                                                        l.strip()).group(1)


    # executing pre-defined sequences
    def init_device(self):

        #self.ui.sprint("Restart adb in case it is a wrong version")
        #self.adb.restart_server()

        self.ui.sprint("If device is defined in config, set it")
        if self.config['device']:
            self.devices = self.adb.get_devices()
            self.adb.set_target_device(self.config['device'])
            self.uad = uiautomator.Device(self.config['device'])

        self.ui.sprint("Sleep until device is booted")
        self.adb.shell_command("while [ `getprop sys.boot_completed | tr -d '\r'` != '1' ] ; do sleep 1; done")

        self.ui.sprint("Uninstall the app if installed")
        self.adb.uninstall(package=self.config['app.name'])

        self.ui.sprint("If there is a pre-boot sequence, execute it")
        # usually required to turn off transitions
        if 'pre-boot' in self.config:
            for cmd in self.config['pre-boot']:
                self.adb.shell_command(cmd)

        self.ui.sprint("Copy necessary files to device")
        self.adb.push_local_file('misc/','/sdcard/')

        self.ui.sprint("Reboot emulator")

        # this code relies on the device being emulator
        self.adb.shell_command("stop")
        self.adb.shell_command("start")

        self.ui.sprint("Sleep until device is booted")
        self.adb.shell_command("while [ `getprop sys.boot_completed | tr -d '\r'` != '1' ] ; do sleep 1; done")

        time.sleep(self.config['timeout'])

        self.ui.sprint("Install the app")
        self.adb.install(pkgapp=self.config['app'])

        self.ui.sprint("If there is a post-boot sequence, execute it")
        # usually required to set a date, etc
        if 'post-boot' in self.config:
            for cmd in self.config['post-boot']:
                self.adb.shell_command(cmd)

        # emulator bug avoidance, some versions of emulator
        # can't set time properly at the boot
        self.ui.sprint("Loop until device time is properly set")
        if  self.config['date'] and self.config['date_assert']:
            tries = 0
            while self.config['date_assert'] not in self.adb.shell_command("date") and tries < 20:
                self.adb.shell_command("date -s "+self.config['date'])
                tries = tries + 1
                time.sleep(1)


        self.ui.sprint("Start the app")
        # the command is hardcoded at the moment
        self.adb.shell_command(' '.join(["am", "start", "-n",
                                         self.config['app.name'] + '/'
                                         + self.config['app.activity']]))

    # start recoding events
    def capture_events(self):

        self.ui.sprint("Device initialization")
        self.init_device()

        # default event device
        dev = '/dev/input/event1'

        self.ui.sprint("Starting adb/getevent to capture events")
        p = subprocess.Popen([self.config['adb'], '-s', self.config['device'],
                              'shell', 'getevent', '-t'], bufsize=-1,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.ui.sprint("Setting file permissions")
        # Prevent the process from blocking
        fd = p.stdout.fileno()
        file_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, file_flags | os.O_NDELAY)

        # home button counter
        hc = 0
        pin = ''

        # loop
        self.ui.sprint("Press STOP button to stop recording...", 1)
        while True:

            # read from getevent stdout
            try:
                pin = p.stdout.readline().strip()
            except:
                pin = ''
                time.sleep(0.0001)

            # if a user pressed home button 3 times, exit
            if self.ui.stop_rec.isSet():

                self.ui.sprint("Exiting...")

                # capture everything
                '''
                self.sequence.append(
                    {
                        "timestamp": self.config['time_threshold']
                        + self.config['time_threshold'] * 0.1,
                        "device": dev,
                        "command": [0, 0, 0]
                    }
                )
                '''

                # Kill the app and the capturing process
                # replace os.kill with p.kill()
                self.kill_app()
                os.kill(p.pid, signal.SIGTERM)
                break
            elif self.ui.btn_back.isSet():
                self.ui.btn_back.clear()
                for ss in self.back_button:
                    self.adb.shell_command('sendevent ' + dev + ' '
                                   + ' '.join(str(c) for c in ss))
                self.ui.sprint("Back button is pressed.", 1)
            elif self.ui.btn_menu.isSet():
                self.ui.btn_menu.clear()
                for ss in self.menu_button:
                    self.adb.shell_command('sendevent ' + dev + ' '
                                   + ' '.join(str(c) for c in ss))
                self.ui.sprint("Menu button is pressed.", 1)

            # skip header or empty lines
            if len(pin) == 0 or pin[0] != '[':
                continue

            # make sure that process didn't die suddenly
            if pin == '' and p.poll() is not None:
                break

            # proceed if an input isn't empty
            if pin != '':

                # get a timestamp
                ts = float(re.search('s*(\d+\.?\d+)]',
                                     pin).group(0)[:-1].strip())

                # separate time stamp, device, and command
                line = pin.split(']')
                line = line[1].split(':')
                dev = line[0].strip()
                ucmd = line[1].strip()
                cmds = ucmd.split()
                cmds = [int(c, 16) for c in cmds]

                # capture everything
                self.sequence.append(
                    {
                        "timestamp": ts,
                        "device": dev,
                        "command": cmds
                    }
                )


                # skip sync output and coordinates (for now)
                #if cmds[1] not in self.config['evdev']['ignore']:

                    # print output (for now)
                    #print(pin)

                '''
                    # count an _emulated_ home button (not a screen one)
                    # presses/releases
                    if cmds[1] == self.config['evdev']['home']:
                        hc += 1
                    else:
                        hc = 0

                    # take a screenshot if necessary
                    if 'screenshots' in self.config:
                        self.adb.shell_command('screencap '
                                               + self.config['screenshots']
                                               + ts + '.raw')


                    # if a user pressed home button 3 times, exit
                    if hc == 6:

                        self.ui.sprint("Exiting...")

                        # capture everything
                        self.sequence.append(
                            {
                                "timestamp": self.config['time_threshold']
                                + self.config['time_threshold'] * 0.1,
                                "device": dev,
                                "command": [0, 0, 0]
                            }
                        )

                        self.kill_app()
                        break
                '''


    def replay_events(self):

        self.ui.sprint("Device initialization")
        self.init_device()
        time.sleep(self.config['timeout'])

        self.ui.sprint("Replaying: Sending events...")

        # first event always passes timestamp threshold
        ts = self.sequence[0]['timestamp'] - (self.config['time_threshold']
                                              + self.config['time_threshold']
                                              * 0.1)

        new_seq = []

        # go through sequences
        for idx, s in enumerate(self.sequence):

            # get a timestamp difference
            ts_dif = s['timestamp'] - ts


            # if difference is too much, just continue
            if ts_dif > self.config['max_timeout']:
                ts_dif = self.config['max_timeout']

            # if it is greater than threshold, and it is a key/tap press,
            # sleep given amount * slowdown factor
            if ts_dif > self.config['time_threshold'] \
               and s['command'][2] == 1 \
               and s['command'][1] not in self.config['evdev']['capture']:
                time.sleep(ts_dif * self.config['slowdown'])
            # otherwise, sleep the minimum amount
            elif ts_dif > self.config['time_threshold']:
                time.sleep(ts_dif)

            # hardcoded for now, checking for presses to dump hierarchy
#            if s['command'][0] == 1 and s['command'][2] == 1 \
#               and s['command'][1] in self.config['evdev']['capture']:
            if s['command'][0] == 3 and s['command'][2] == 0 \
               and s['command'][1] == 57:
                s['dump'] = self.uad.dump()
                s['window_info'] = self.adb.shell_command("dumpsys "
                                                          + "window windows")

                #print self.uad.info['currentPackageName']

                # make screenshot if necessary
                if 'screenshot' in self.config:
                    self.adb.shell_command(self.config['screenshot']['cmd']
                                           + ' '
                                           + self.config['screenshot']['dir']
                                           + '{:.6f}'.format(s['timestamp'])
                                           + self.config['screenshot']['ext'])

            # if the event is 'non-essential' one, do nothing
            else:
                s['dump'] = None
                s['window_info'] = None

            #print(idx,'sendevent ' + s['device'] + ' ' + ' '.join(str(c) for c in s['command']))
            # execute the event
            self.adb.shell_command('sendevent ' + s['device'] + ' '
                                   + ' '.join(str(c) for c in s['command']))

            # change timestamp
            ts = s['timestamp']

            # for now dumps modified sequence to a file
            new_seq.append(s)

#        self.adb.shell_command('sendevent ' + s['device'] + ' '
#                               + ' '.join(str(c) for c in s['command']))

        # save modified sequence
        self.sequence_replay = new_seq

        # make sure that everything is replayed correctly
        self.ui.sprint('Ending replay')
        time.sleep(self.config['timeout'])

        # save code coverage information
        self.ui.sprint('Saving code coverage information')
        self.adb.shell_command(' '.join(['am','broadcast','-a',
                               self.config['app.name'] + '.DUMP_COVERAGE']))
        self.kill_app()

#        self.__file = self.__file.replace('orig_', 'mod_')
#        json.dump(new_seq, open(self.__file, 'wb'), indent=4)

    def kill_app(self):
        self.ui.sprint('Stopping the app')
        self.adb.shell_command(' '.join(['am force-stop ',
                                         self.config['app.name']]))

    # save captured sequence as a given json file
    def save_sequence(self, fn = None):

        ufn = str(uuid.uuid4())
        if fn:
            self.__file = fn
        else:
            dirname = self.config['tests'] + '/' + self.app_name

            try:
                os.makedirs(dirname)
            except:
                pass

            self.__file =  dirname + '/' + ufn + '.json'


        if len(self.sequence_replay):
            json.dump(self.sequence_replay, open(self.__file, 'wb'),
                      indent=4)
        else:
            json.dump(self.sequence, open(self.__file, 'wb'),
                      indent=4)

        self.adb.get_remote_file('/mnt/sdcard/coverage.ec',
                                 self.__file.replace('.json','.ec'))

        if 'screenshot' in self.config:
            #try:
            #    os.mkdir(self.__file.replace('.json',''))
            #except:
            #    pass
            self.adb.get_remote_file('/mnt/sdcard/ss',
                                 self.__file.replace('.json',''))

        return ufn

    # load captured sequence from a given json file
    def load_sequence(self, fn):
        self.__file = fn
        self.sequence = json.load(open(fn))


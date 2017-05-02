#!/bin/env python
# -*- coding: utf-8 -*-
import sys
import subprocess
import misc
import gi
import os
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk, GLib, GObject
from atest import testDevice

# panel for control during capturing events
class ctrlEmulator(Gtk.Window):

    def __init__(self, main):

        myFA = "FontAwesome 12"

        # stop button clicked
        def tbutton_clicked(self):
            main.sprint("Stopping the recording...")
            main.stop_rec.set()

        # menu button clicked
        def mbutton_clicked(self):
            main.sprint("Pressing Menu button...")
            main.btn_menu.set()

        # back button clicked
        def bbutton_clicked(self):
            main.sprint("Pressing Back button...")
            main.btn_back.set()


        Gtk.Window.__init__(self, title="Emulator Controls")
        Gtk.Window.set_default_size(self, 20, 20)

        grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=True)
        self.add(grid)

        # define buttons
        mbutton = Gtk.Button(u"\uf0c9") # menu
        bbutton = Gtk.Button(u"\uf060") # back
        tbutton = Gtk.Button(u"\uf04d") # stop

        mbutton.modify_font(Pango.FontDescription(myFA))
        mbutton.set_tooltip_text("Menu")
        mbutton.connect("clicked", mbutton_clicked)

        bbutton.modify_font(Pango.FontDescription(myFA))
        bbutton.set_tooltip_text("Back")
        bbutton.connect("clicked", bbutton_clicked)

        tbutton.modify_font(Pango.FontDescription(myFA))
        tbutton.set_tooltip_text("Stop Recording a Test Case")
        tbutton.connect("clicked", tbutton_clicked)

        grid.attach(mbutton             , 0, 3, 1, 1)
        grid.attach(bbutton             , 0, 2, 1, 1)
        grid.attach(Gtk.Separator()     , 0, 1, 1, 1)
        grid.attach(tbutton             , 0, 0, 1, 1)

        style = Gtk.CssProvider()

        css = \
        """
        #ceCtrl {
            font-family: Ubuntu;
            font-size: 12px;
            background: transparent;
            color: #ddd;
        }
        #ceCtrl GtkButton {
            box-shadow: 0 0 0 0;
            padding: 10px 13px;
            margin: 0;
            background: #eee;
            border-radius: 0px;
        }
        """

        style.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                style,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )




# main panel for control
class myWindow(Gtk.Window):

    myFA = "FontAwesome 12"
    test_config = None
    myTest = None
    win2 = None

    # button events
    stop_rec = threading.Event()
    btn_back = threading.Event()
    btn_menu = threading.Event()

    test_combo = Gtk.ComboBoxText()

    sbar = Gtk.Statusbar()
    sbar_id = sbar.get_context_id("sbar")

    # define buttons on the panel
    rbutton = Gtk.Button(u"\uf111") # record
    pbutton = Gtk.Button(u"\uf04b") # play
    sbutton = Gtk.Button(u"\uf0c7") # save
    cbutton = Gtk.Button(u"\uf0e2") # clear
    tbutton = Gtk.Button(u"\uf04d") # stop
    bbutton = Gtk.Button(u"\uf011") # power

    # show the second panel during capture
    def show(self):
        self.win2 = ctrlEmulator(self)
        self.win2.set_name('ceCtrl')
        self.win2.connect("delete-event", Gtk.main_quit)
        self.win2.set_accept_focus(False)
        self.win2.move(490, 45)
        self.win2.show_all()

    # hide the second panel
    def hide(self):
        self.win2.hide()
        self.win2.destroy()


    def __init__(self):

        Gtk.Window.__init__(self, title=sys.argv[1])
        Gtk.Window.set_default_size(self, 400,60)

        #self.show()

        self.grid = Gtk.Grid(column_homogeneous=True, row_homogeneous=True)
        self.add(self.grid)

        self.test_combo.connect("changed", self.on_test_combo_changed)

        self.stop_rec.clear()

        apps = misc.get_apps()

        for app in apps:
            self.test_combo.append_text(app.replace('conf/','').replace('.json',''))

        self.test_combo.append_text('- Pick Your App -')
        self.test_combo.set_active(len(apps))

        self.sbar.set_name("sbar")

        self.rbutton.set_tooltip_text("Record a Test Case")
        self.rbutton.modify_font(Pango.FontDescription(self.myFA))
        self.rbutton.set_name("rec")
        self.rbutton.connect("clicked", self.rbutton_clicked)

        self.pbutton.modify_font(Pango.FontDescription(self.myFA))
        self.pbutton.set_tooltip_text("Replay the Recorded Test Case")
        self.pbutton.connect("clicked", self.pbutton_clicked)
        self.pbutton.set_sensitive(False)

        self.sbutton.modify_font(Pango.FontDescription(self.myFA))
        self.sbutton.set_tooltip_text("Save the Recorded Test Case")
        self.sbutton.connect("clicked", self.sbutton_clicked)
        self.sbutton.set_sensitive(False)

        self.cbutton.modify_font(Pango.FontDescription(self.myFA))
        self.cbutton.set_tooltip_text("Clear the Recorded Test Case")
        self.cbutton.connect("clicked", self.cbutton_clicked)
        self.cbutton.set_sensitive(False)

        self.tbutton.modify_font(Pango.FontDescription(self.myFA))
        self.tbutton.set_tooltip_text("Stop Recording a Test Case")
        self.tbutton.connect("clicked", self.tbutton_clicked)
        self.tbutton.set_sensitive(False)

        self.bbutton.modify_font(Pango.FontDescription(self.myFA))
        self.bbutton.set_tooltip_text("Restart Virtual Machine")
        self.bbutton.connect("clicked", self.bbutton_clicked)

        self.sbar.push(self.sbar_id,"Ready.")

        self.grid.attach(self.test_combo, 0, 0, 3, 1)
        self.grid.attach(self.rbutton   , 3, 0, 1, 1)
        #self.grid.attach(self.tbutton   , 0, 1, 1, 1)
        self.grid.attach(self.pbutton   , 0, 1, 1, 1)
        self.grid.attach(self.sbutton   , 1, 1, 1, 1)
        self.grid.attach(self.cbutton   , 2, 1, 1, 1)
        self.grid.attach(self.bbutton   , 3, 1, 1, 1)
        self.grid.attach(self.sbar      , 0, 2, 4, 1)

        style = Gtk.CssProvider()

        css = \
        """
        #aCtrl {
            font-family: Ubuntu;
            font-size: 12px;
            background: transparent;
            color: #ddd;
        }
        #aCtrl GtkButton {
            box-shadow: 0 0 0 0;
            background: #eee;
            border-radius: 0px;
        }
        #sbar {
            padding: 0;
            margin: 0;
            font-size: 8px;
        }
        #rec {
            color: #f00;
        }
        #rec:insensitive {
            color: #f99;
        }
        """

        style.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                style,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    # status bar messages
    def sprint(self, msg, status=0):
        s = { 0: '[WAIT]', 1: '[READY]'}
        def func(msg):
            self.sbar.pop(self.sbar_id)
            self.sbar.push(self.sbar_id, s[status]+' '+msg)
            return False;

        GLib.idle_add(func, msg)

    # power button clicked
    def bbutton_clicked(self, button):
        # change it to subprocess.call to avoid zombie processes
        p = subprocess.Popen(["vnc4server","-kill",os.environ['DISPLAY']],
                             bufsize=-1, stdout = subprocess.PIPE,
                             stderr= subprocess.PIPE)

    # play button clicked
    def pbutton_clicked(self, button):
        def func():
            self.myTest.replay_events()
            self.enable_buttons()
            #GLib.idle_add(self.hide)
            self.sprint("Replay complete.", 1)

        self.sprint("Replaying the recorded test...")
        self.disable_buttons()
        #GLib.idle_add(self.show)
        t = threading.Thread(target=func)
        t.start()

    # record button clicked
    def rbutton_clicked(self, button):
        def func():
            self.myTest = testDevice(self)
            self.myTest.capture_events()
            self.enable_buttons(self.sbutton, self.tbutton)
            GLib.idle_add(self.hide)
            self.sprint("Recording complete.", 1)

        self.sprint("Recording a test")
        self.stop_rec.clear()
        self.disable_buttons(self.tbutton)
        GLib.idle_add(self.show)
        t = threading.Thread(target=func)
        t.start()

    # save button clicked
    def sbutton_clicked(self, button):
        def func():
            if len(self.myTest.sequence_replay):
                ufn = self.myTest.save_sequence()
                self.sprint("Saved unique id: %s." % str(ufn), 1)

                def func2():
                    self.pbutton.set_sensitive(False)
                    self.sbutton.set_sensitive(False)
                    self.cbutton.set_sensitive(False)
                    return False
                GLib.idle_add(func2)
                self.myTest = None

            else:
                self.sprint("Please replay the test before saving", 1)

        self.sprint("Saving the recorded test...")
        t = threading.Thread(target=func)
        t.start()

    # clear button clicked
    def cbutton_clicked(self, button):
        self.sprint("Clearing the recorded test...")
        self.pbutton.set_sensitive(False)
        self.sbutton.set_sensitive(False)
        self.cbutton.set_sensitive(False)
        self.myTest = None
        self.sprint('Clear complete.', 1)

    # stop button clicked
    def tbutton_clicked(self, button):
        self.sprint("Stopping the recording...")
        self.stop_rec.set()

    # app selected
    def on_test_combo_changed(self, combo):
        text = combo.get_active_text()

        if text != None:
            self.sprint("Selected: %s" % text, 1)
            self.rbutton.set_sensitive(True)
            self.test_config = "conf/"+text+".json"

        if text == "- Pick Your App -":
            self.sprint("Selected: None", 1)
            self.rbutton.set_sensitive(False)
            self.test_config = None

    # disable certain buttons during capture/replay
    def disable_buttons(self, *args):
        def func():
            self.test_combo.set_sensitive(False)
            self.rbutton.set_sensitive(False)
            self.pbutton.set_sensitive(False)
            self.sbutton.set_sensitive(False)
            self.cbutton.set_sensitive(False)
            for a in args:
                a.set_sensitive(True)

            return False;

        GLib.idle_add(func)

    # re-enable buttons
    def enable_buttons(self, *args):
        def func():
            self.test_combo.set_sensitive(True)
            self.rbutton.set_sensitive(True)
            self.pbutton.set_sensitive(True)
            self.sbutton.set_sensitive(True)
            self.cbutton.set_sensitive(True)
            for a in args:
                a.set_sensitive(False)

            return False;

        GLib.idle_add(func)

# main thread
def app_main():

    # set window parameters
    win = myWindow()
    win.set_name('aCtrl')
    win.connect("delete-event", Gtk.main_quit)
    win.move(50, 815)
    win.show_all()

# start GUI
GObject.threads_init()

app_main()
Gtk.main()

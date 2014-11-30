#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import dbus, dbus.mainloop.glib
import calendar
import argparse
import gobject
import signal
import time
import gtk

arg_parser = argparse.ArgumentParser(description='awehamster is a bridge between Hamster Time Tracker and Awesome WM.')
arg_parser.add_argument('what', nargs='?', default='start',
                        help='Action to execute. Default is gui. Should be daemon, start or stop.')
args = arg_parser.parse_args()


class AwesomeHamsterProxy:
    def __init__(self):
        self.bus = dbus.SessionBus()

        proxyHamster = self.bus.get_object('org.gnome.Hamster', '/org/gnome/Hamster')
        self.ifaceHamster = dbus.Interface(proxyHamster, 'org.gnome.Hamster')

    def get_activities(self):
        return self.ifaceHamster.GetActivities('')

    def get_todays_facts(self):
        return self.ifaceHamster.GetTodaysFacts()

    def add_fact(self, text):
        self.ifaceHamster.AddFact(text, 0, 0, False)

    def stop(self):
        self.ifaceHamster.StopTracking(0)





class AwesomeHamsterGui():
    def __init__(self):
        self.proxyHamster = AwesomeHamsterProxy()
        activities = self.proxyHamster.get_activities()

        self.activitiesList = gtk.ListStore(str)
        self.maxLen = 0
        for act in activities:
            act_label = act[0]
            if act[1] != '':
                act_label = act[0] + '@' + act[1]

            if len(act_label) > self.maxLen:
                self.maxLen = len(act_label)
                self.activitiesList.append([act_label])


    def _match_anywhere(self, completion, entrystr, iter, data):
        modelstr = completion.get_model()[iter][0]
        return entrystr in modelstr


    def _on_entry_activate(self, entry):
        text = entry.get_text()
        if text != '':
            self.proxyHamster.add_fact(text)
            self.dialog.destroy()

    def run(self):
        label = gtk.Label("New activity: ")
        hBox = gtk.HBox()

        entryCompletion = gtk.EntryCompletion()
        entryCompletion.set_model(self.activitiesList)
        entryCompletion.set_text_column(0)
        entryCompletion.set_match_func(self._match_anywhere, None)

        entry = gtk.Entry()
        entry.set_completion(entryCompletion)
        entry.set_width_chars(self.maxLen + 5)
        entry.connect("activate", self._on_entry_activate)

        self.dialog = gtk.Dialog("New activity",
                                 None,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        hBox.pack_start(label)
        hBox.pack_start(entry)
        self.dialog.vbox.pack_start(hBox)
        label.show()
        entry.show()
        hBox.show()
        self.dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.dialog.run()


class AwesomeHamster(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)

        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.proxyHamster = AwesomeHamsterProxy()
        self.proxyHamster.bus.add_signal_receiver(self._on_facts_changed, 'FactsChanged', 'org.gnome.Hamster')

        proxyAwesome = self.proxyHamster.bus.get_object('org.naquadah.awesome.awful', '/')
        self.ifaceAwesome = dbus.Interface(proxyAwesome, 'org.naquadah.awesome.awful.Remote')


    def _pretty_format(self, number):
        if number < 10:
            return "0" + str(number)
        else:
            return str(number)

    def _on_facts_changed(self):
        self._refresh()

    def _refresh(self):
        startTime = 0
        facts = self.proxyHamster.get_todays_facts()

        if len(facts) > 0:
            f = facts[-1]
            startTime = f[1]
            endTime = f[2]
            currentTime = calendar.timegm(time.localtime())
            elapsedTime = currentTime - startTime

        if startTime == 0 or endTime != 0:
            print "No activity"
            self.ifaceAwesome.Eval('myawehamsterbox:set_text(" No activity ")')

        else:
            minutes = elapsedTime / 60
            hours = minutes / 60
            minutes = minutes - (hours * 60)
            activity = (f[4]).encode("utf-8")
            category = (f[6]).encode("utf-8")
            print "%s@%s %s:%s" % (activity, category, self._pretty_format(hours), self._pretty_format(minutes))
            self.ifaceAwesome.Eval('myawehamsterbox:set_text(" %s@%s %s:%s ")' % (activity, category, self._pretty_format(hours), self._pretty_format(minutes)))

        return True

    def shutdown(self, signal, frame):
        print "Kthxbye"
        self.ifaceAwesome.Eval('myawehamsterbox:set_text(" %s ")' % (self.old_text))
        self.loop.quit()

    def run(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        gobject.timeout_add_seconds(60, self._refresh)

        # self.old_text = self.ifaceAwesome.Eval('myawehamsterbox:get_text()')
        self.old_text = ' no hamster :( '
        print self.old_text

        self._refresh()
        self.loop = gobject.MainLoop()
        self.loop.run()


if __name__=='__main__':
    if args.what == 'daemon':
        awehamster = AwesomeHamster()
        awehamster.run()

    elif args.what == 'stop':
        hamsterProxy = AwesomeHamsterProxy()
        hamsterProxy.stop()

    else:
        # start
        ahgui = AwesomeHamsterGui()
        ahgui.run()

awesome-hamster
===============

Bridge between Hamster Time Tracker and Awesome WM

Dependencies
============

 - Awesome WM
 - Hasmter Time Tracker (usually called hamster-applet in most
   distros)
 - Python 2
 - pygtk
 - python-dbus
 - python-gobject


Copying the scripts to a place you like
=======================================

Put both scripts (awehamster.py and awehamster.lua) in some
directory of your preference (for this document, I'm going to assume
you've put them in $HOME/bin), and give them the execution permission
bit.

    # cp awehamster.py awehamster.lua ~/.config/awesome/plugins
    # chmod u+x ~/.config/awesome/plugins/awehamster.py


Creating a placeholder in Awesome WM
====================================

AwesomeHamster is not an actual awesome WM widget. Instead, it uses a
textbox placeholder, changing dynamically its contents via Dbus. Thus
you need to create such a placeholder in your wibox. Try adding this
in your "rc.lua" somewhere near "mytextbox" and "mytextclock" definition.

    myawehamsterbox = require('plugins.awehamster')
    myawehamsterbox.init({pyscript = '~/.config/awesome/plugins/awehamster.py'})

And now you must add this widget to your wibox. Change its definition
to look like this:

    -- Create the wibox
    mywibox[s] = awful.wibox({ position = "top", screen = s })

    -- Widgets that are aligned to the left
    local left_layout = wibox.layout.fixed.horizontal()
    left_layout:add(mylayoutbox[s])
    left_layout:add(mytaglist[s])
    left_layout:add(mypromptbox[s])

    -- Widgets that are aligned to the right
    local right_layout = wibox.layout.fixed.horizontal()
    right_layout:add(myawehamsterbox.label)
    -- On ne peut avoir qu'un systray apparement
    if s == 1 then right_layout:add(wibox.widget.systray()) end
    right_layout:add(mytextclock)

    -- Now bring it all together (with the tasklist in the middle)
    local layout = wibox.layout.align.horizontal()
    layout:set_left(left_layout)
    layout:set_middle(mytasklist[s])
    layout:set_right(right_layout)

    mywibox[s]:set_widget(layout)


Defining some convenient shortcuts
==================================

I like to use "Mod+s" to stop tracking, and "Mod+a" to launch the gui
for selecting a new activity. This is what I got in my "rc.lua":

    awful.key({ modkey,           }, "a", myawehamsterbox.add_fact),
    awful.key({ modkey,           }, "s", myawehamsterbox.stop_fact),


Starting it with your session
=============================

Add this to the end of your "rc.lua":

    awful.util.spawn_with_shell(myawehamsterbox.bin.." daemon")

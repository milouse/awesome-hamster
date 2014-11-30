local wibox = require('wibox')
local awful = require('awful')

local awehamster = {
   label = wibox.widget.textbox(),
   bin = './awehamster.py'
}

function awehamster.stop_fact()
   awful.util.spawn(awehamster.bin.." stop")
end

function awehamster.add_fact()
   awful.util.spawn(awehamster.bin.." start")
end

function awehamster.init(args)
   local args = args or {}
   awehamster.bin = args.pyscript or awehamster.bin

   awehamster.label:set_text(' No hamster :( ')
   awehamster.label:connect_signal(
      "button::press",
      awehamster.stop_fact)
end

return awehamster

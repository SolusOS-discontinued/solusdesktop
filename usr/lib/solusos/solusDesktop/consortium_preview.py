#!/usr/bin/env python
import pygtk
import gtk
import dbus
import dbus.service
import consortium

from dbus.mainloop.glib import DBusGMainLoop

class ConsortiumThemePreview(dbus.service.Object):

   def __init__(self):
	bus_name = dbus.service.BusName('com.solusos.consortiumthemepreview', bus=dbus.SessionBus())

	# make plug, reparent
	self.plug = gtk.Plug(0L)
	self.plug_id = self.plug.get_id()

	self.plug.connect("destroy", gtk.main_quit)

	self.plug.connect("embedded", self.create_ui)

	self.theme = None

	dbus.service.Object.__init__(self, bus_name, '/com/solusos/consortiumthemepreview')

   def create_ui(self, some_event):
	self.preview = consortium.Preview()
	self.plug.add(self.preview)
	self.plug.show_all()	
	return

   @dbus.service.method(dbus_interface = "com.solusos.consortiumthemepreview", in_signature = None, out_signature = 'i')
   def get_plug_id(self):
	return self.plug_id

   @dbus.service.method(dbus_interface = "com.solusos.consortiumthemepreview", in_signature = 's', out_signature = None)
   def set_theme_name(self, theme_name):
	if self.theme is not None:
		self.theme.free()
	theme = consortium.theme_load(theme_name)
	self.preview.set_title("%s theme" % theme_name)
	self.preview.set_theme(theme)

	return


if __name__ == "__main__":
	DBusGMainLoop(set_as_default=True)
	myservice = ConsortiumThemePreview()
	gtk.main()


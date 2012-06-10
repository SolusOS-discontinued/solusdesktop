import gi

from gi.repository import Gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

class ThemePreview(dbus.service.Object):

   def __init__(self):
	bus_name = dbus.service.BusName('com.solusos.themepreview', bus=dbus.SessionBus())
	self.builder = Gtk.Builder()
	self.builder.add_from_file("./theme_preview.ui")
	self.get_widget = self.builder.get_object

	# make plug, reparent
	self.plug = Gtk.Plug()
	self.plug_id = self.plug.get_id()

	self.plug.connect("destroy", Gtk.main_quit)

	self.plug.connect("embedded", self.create_ui)

	dbus.service.Object.__init__(self, bus_name, '/com/solusos/themepreview')

   def create_ui(self, some_event):
	print "Yo. I iz embedded"
	iface = self.get_widget("box1")
	iface.unparent()

	self.plug.add(iface)
	self.plug.show_all()

   @dbus.service.method(dbus_interface = "com.solusos.themepreview", in_signature = None, out_signature = 'i')
   def get_plug_id(self):
	return self.plug_id

   @dbus.service.method(dbus_interface = "com.solusos.themepreview", in_signature = 's', out_signature = None)
   def set_theme_name(self, theme_name):
	settings = self.plug.get_settings()
	settings.set_string_property("gtk-theme-name", theme_name, "gtkrc:0")


if __name__ == "__main__":
	DBusGMainLoop(set_as_default=True)
	myservice = ThemePreview()
	Gtk.main()


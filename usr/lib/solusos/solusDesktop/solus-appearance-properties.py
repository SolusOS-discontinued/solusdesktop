#!/usr/bin/env python

import gi
from gi.repository import Gtk, GConf, GdkPixbuf

''' Helper class to make side pages :) '''
class SidePage:
    def __init__(self, notebook_index, name, icon):
        self.notebook_index = notebook_index
        self.name = name
        self.icon = icon


class AppearanceWindow:

   ''' Side-view navigation '''
   def side_view_nav(self, widg):
	items = widg.get_selected_items()
	if(len(items) < 1):
		return
	item = widg.get_selected_items()[0]
	selected = int(str(item))
	print selected
	self.get_widget("notebook1").set_current_page(selected)

   def __init__(self):
	self.builder = Gtk.Builder()
	self.builder.add_from_file('/usr/lib/solusos/solusDesktop/solusDesktop.ui')

	# Add a hook for getting objects out of the GtkBuilder
	self.get_widget = self.builder.get_object

	# Our main window
	self.window = self.get_widget("main_window")
	self.window.set_title("SolusOS Appearance")
	self.window.connect('destroy', Gtk.main_quit)

	# setup the side pages
        side_gnome_desktop_options = SidePage(0, "Desktop", "user-desktop")
        side_gnome_windows = SidePage(1, "Windows", "window-new")
        side_gnome_interface = SidePage(2, "Interface", "preferences-desktop")
        side_gnome_effects = SidePage(3, "Theme", "preferences-other")
        side_wallpaper = SidePage(3, "Wallpaper", "preferences-desktop-theme")
        self.sidePages = [side_gnome_desktop_options, side_gnome_windows, side_gnome_interface, side_gnome_effects]

	self.iconTheme = Gtk.IconTheme.get_default()

	# liststore for the side thingy
	self.store = Gtk.ListStore(str, GdkPixbuf.Pixbuf.__gtype__)
	iter_first = None
	for page in self.sidePages:
		img = self.iconTheme.load_icon(page.icon, 36, Gtk.IconLookupFlags.GENERIC_FALLBACK)
		tmpiter = self.store.append([page.name, img])
		# set the iter to the first item so we can select it :)
		if iter_first is None:
			iter_first = tmpiter

        # set up the side view - navigation.
        self.get_widget("side_view").set_text_column(0)
        self.get_widget("side_view").set_pixbuf_column(1)
        self.get_widget("side_view").set_model(self.store)
        #self.get_widget("side_view").select_path(iter_first)
        self.get_widget("side_view").connect("selection_changed", self.side_view_nav )

########
# MAIN #
########
if __name__ == "__main__":

	win = AppearanceWindow()

	Gtk.main()

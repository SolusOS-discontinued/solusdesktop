#!/usr/bin/env python

import gi
from gi.repository import Gtk, GConf, GdkPixbuf
import gettext


gettext.install("solusdesktop", "/usr/share/solusos/locale")

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


        # i18n
        self.get_widget("label_desktop_icons").set_markup("<b>" + _("Desktop icons") + "</b>")
        self.get_widget("label_performance").set_markup("<b>" + _("Performance") + "</b>")
        self.get_widget("label_appearance").set_markup("<b>" + _("Appearance") + "</b>")
        self.get_widget("label_icons").set_markup("<b>" + _("Icons") + "</b>")
        self.get_widget("label_context_menus").set_markup("<b>" + _("Context menus") + "</b>")
        self.get_widget("label_toolbars").set_markup("<b>" + _("Toolbars") + "</b>")
        self.get_widget("caption_desktop_icons").set_markup("<small><i><span foreground=\"#555555\">" + _("Select the items you want to see on the desktop:") + "</span></i></small>")

        self.get_widget("checkbox_computer").set_label(_("Computer"))
        self.get_widget("checkbox_home").set_label(_("Home"))
        self.get_widget("checkbox_network").set_label(_("Network"))
        self.get_widget("checkbox_trash").set_label(_("Trash"))
        self.get_widget("checkbox_volumes").set_label(_("Mounted Volumes"))

        self.get_widget("checkbutton_resources").set_label(_("Don't show window content while dragging them"))
        self.get_widget("checkbox_compositing").set_label(_("Use Gnome compositing"))
        self.get_widget("checkbutton_titlebar").set_label(_("Use system font in titlebar"))

        self.get_widget("label_layouts").set_text(_("Buttons layout:"))

        self.get_widget("checkbutton_menuicon").set_label(_("Show icons on menus"))
        self.get_widget("checkbutton_button_icons").set_label(_("Show icons on buttons"))
        self.get_widget("checkbutton_im_menu").set_label(_("Show Input Methods menu in context menus"))
        self.get_widget("checkbutton_unicode").set_label(_("Show Unicode Control Character menu in context menus"))

        self.get_widget("label_tool_icons").set_text(_("Buttons labels:"))
        self.get_widget("label_icon_size").set_text(_("Icon size:"))

########
# MAIN #
########
if __name__ == "__main__":

	win = AppearanceWindow()

	Gtk.main()

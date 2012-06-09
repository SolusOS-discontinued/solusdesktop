#!/usr/bin/env python

import gi
from gi.repository import Gtk, GConf, GdkPixbuf, Gio
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
	#self.builder.add_from_file('/usr/lib/solusos/solusDesktop/solusDesktop.ui')
	self.builder.add_from_file('./interface.ui')
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
        side_gnome_theme = SidePage(3, "Theme", "preferences-other")
        side_gnome_fonts = SidePage(4, "Fonts", "font-x-generic")
        self.sidePages = [side_gnome_desktop_options, side_gnome_windows, side_gnome_interface, side_gnome_theme, side_gnome_fonts]

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
        self.get_widget("caption_desktop_icons").set_markup("<small><i><span foreground=\"#555555\">" + _("Select the items you want to see on the desktop:") + "</span></i></small>")

        self.get_widget("label_computer").set_label(_("Computer"))
        self.get_widget("label_home").set_label(_("Home"))
        self.get_widget("label_network").set_label(_("Network"))
        self.get_widget("label_trash").set_label(_("Trash"))
        self.get_widget("label_volumes").set_label(_("Mounted Volumes"))

        self.get_widget("checkbutton_resources").set_label(_("Don't show window content while dragging them"))
        self.get_widget("checkbox_compositing").set_label(_("Use Gnome compositing"))
        self.get_widget("checkbutton_titlebar").set_label(_("Use system font in titlebar"))

        self.get_widget("label_layouts").set_text(_("Buttons layout:"))

        self.get_widget("label_menuicon").set_label(_("Show icons on menus"))
        self.get_widget("label_button_icons").set_label(_("Show icons on buttons"))
        self.get_widget("label_im_menu").set_label(_("Show Input Methods menu"))
        self.get_widget("label_unicode").set_label(_("Show Unicode Control Character menu"))

	# Desktop (nautilus) settings
	self.desktop_settings = Gio.Settings.new("org.gnome.nautilus.desktop")
        # Desktop page
        self.init_switch(self.desktop_settings, "computer-icon-visible", "switch_computer")
        self.init_switch(self.desktop_settings, "home-icon-visible", "switch_home")
        self.init_switch(self.desktop_settings, "network-icon-visible", "switch_network")
        self.init_switch(self.desktop_settings, "trash-icon-visible", "switch_trash")
        self.init_switch(self.desktop_settings, "volumes-visible", "switch_volumes")

	# Interface settings
	self.gnome_settings = Gio.Settings.new("org.gnome.desktop.interface")
        # interface page
        self.init_switch(self.gnome_settings, "menus-have-icons", "switch_menuicon")
        self.init_switch(self.gnome_settings, "show-input-method-menu","switch_im_menu")
        self.init_switch(self.gnome_settings, "show-unicode-menu", "switch_unicode")
        self.init_switch(self.gnome_settings, "buttons-have-icons", "switch_button_icons")

	self.demo_create()


   ''' Refresh the demo preview '''
   def demo_create(self):
	tbar = self.get_widget("toolbar_demo")
	stocks = [ Gtk.STOCK_NEW, Gtk.STOCK_OPEN, Gtk.STOCK_SAVE, Gtk.STOCK_PRINT ]

	for stock in stocks:
		item = Gtk.ToolButton(stock)
		tbar.add(item)

	demo_area = self.get_widget("box_demo")
	setts = demo_area.get_settings()
	setts.set_string_property("gtk-theme-name", "Adwaita", "gtkrc:0")
	tbar.show_all()

   ''' Helper function, initialises a checkbox to a setting in gsettings '''
   def init_checkbox(self, settings, key, widget_name):
	widget = self.get_widget(widget_name)
	value = settings.get_boolean(key)
	widget.set_active(value)

	def the_checkbox_cb(sets,key):
		value_new = sets.get_boolean(key)
		widget.set_active(value_new)

	def go_change_it(wid):
		settings.set_boolean(key, widget.get_active())
	widget.connect("clicked", go_change_it)
	settings.connect("changed::%s" % key, the_checkbox_cb)

   ''' Helper function, initialises a checkbox to a setting in gsettings '''
   def init_switch(self, settings, key, widget_name):
	widget = self.get_widget(widget_name)
	value = settings.get_boolean(key)
	widget.set_active(value)

	def the_switch_cb(sets,key):
		value_new = sets.get_boolean(key)
		widget.set_active(value_new)

	def go_change_switch(wid,data=None):
		print "Switched!"
		settings.set_boolean(key, widget.get_active())

	widget.connect("notify::active", go_change_switch)
	settings.connect("changed::%s" % key, the_switch_cb)

   ''' Helper function, initialises a combobox to a gsettings value and binds it '''
   def init_combobox(self, settings, key, widget_name):
	widget = self.get_widget(widget_name)
	value = settings.get_string(key)

	model = widget.get_model()

	# somethin' changed!
	def the_combo_cb(sets,key):
		value_new = sets.get_string(key)
		row=0
		for i in model:
			row+=1
			if value == i[1]:
				widget.set_active(row)

	def go_change_combo(wid,data=None):
		selected = widget.get_active_iter()
		if selected is not None:
			value = model[selected][1]
			settings.set_string(key, value)

	row = 0
	# set the row to the currently used setting
	for i in model:
		print "key: %s, value=%s, found=%s" % (key,value,i[1])
		row+=1
		if value == i[1]:
			widget.set_active(row)
	
	settings.connect("changed::%s" % key, the_combo_cb)
	widget.connect("changed", go_change_combo)

########
# MAIN #
########
if __name__ == "__main__":

	win = AppearanceWindow()

	Gtk.main()

#!/usr/bin/env python

import gi
from gi.repository import Gtk, GConf, GdkPixbuf, Gio
import gettext
import dbus
import os
import os.path

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
	self.builder.add_from_file('/usr/lib/solusos/solusDesktop/interface.ui')
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

        self.get_widget("label_resources").set_label(_("Low resource usage (limited usability)"))
        self.get_widget("label_compositing").set_label(_("Desktop compositing"))
        self.get_widget("label_systemfont").set_label(_("System font on titlebar"))

        self.get_widget("label_wm_layout").set_label(_("Buttons layout:"))

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

	# Theme page
	self.build_themes_list()
	self.init_combobox(self.gnome_settings, "gtk-theme", "combobox_widget_theme")

	# Icons
	self.build_icons_list()
	self.init_combobox(self.gnome_settings, "icon-theme", "combobox_icon_theme")
	self.build_preview()

	# metacity stuff
	self.metacity_settings = GConf.Client.get_default()
	## Tell GConf we're interested in these keys
	self.metacity_settings.add_dir("/apps/metacity/general", GConf.ClientPreloadType.PRELOAD_NONE)

	self.init_switch_gconf(self.metacity_settings, "/apps/metacity/general/reduced_resources", "switch_resources")
	self.init_switch_gconf(self.metacity_settings, "/apps/metacity/general/compositing_manager", "switch_composite")
	self.init_switch_gconf(self.metacity_settings, "/apps/metacity/general/titlebar_uses_system_font", "switch_wm_font")

	# combobox fun for metacity theme layouts
	# Metacity button layouts..
	layouts = Gtk.ListStore(str, str)
	layouts.append([_("Traditional style (Right)"), "menu:minimize,maximize,close"])
	layouts.append([_("Mac style (Left)"), "close,minimize,maximize:"])
	self.get_widget("combobox_wm_layout").set_model(layouts)
	box = self.get_widget("combobox_wm_layout")
	renderer_text = Gtk.CellRendererText()
	box.pack_start(renderer_text, True)
	box.add_attribute(renderer_text, "text", 0)
	self.init_gconf_combobox(self.metacity_settings, "/apps/metacity/general/button_layout", "combobox_wm_layout", abnormal=True)

   ''' Initialise the preview area '''
   def build_preview(self):
	bus = dbus.SessionBus()
	preview_service = bus.get_object("com.solusos.themepreview", "/com/solusos/themepreview")
	get_plug = preview_service.get_dbus_method("get_plug_id", "com.solusos.themepreview")
	plug_id = get_plug()

	# we can now embed the preview widget as we got its plug id :)
	socket = Gtk.Socket()
	self.get_widget("box_preview").add(socket)
	socket.add_id(plug_id)
	self.get_widget("box_preview").show_all()

	# ThemePreview methods
	theme_switch = preview_service.get_dbus_method("set_theme_name", "com.solusos.themepreview")
	icon_switch = preview_service.get_dbus_method("set_icon_name", "com.solusos.themepreview")
	def change_theme_cb(wid,data=None):
		active = wid.get_active_iter()
		item = wid.get_model()[active][0]
		# do we enable the apply button?
		old_value = self.gnome_settings.get_string("gtk-theme")
		if old_value != item:
			self.get_widget("button_widget_apply").set_sensitive(True)
		else:
			self.get_widget("button_widget_apply").set_sensitive(False)
		theme_switch(item)

	def change_icons_cb(wid,data=None):
		active = wid.get_active_iter()
		item = wid.get_model()[active][0]
		# do we enable the apply button?
		old_value = self.gnome_settings.get_string("icon-theme")
		if old_value != item:
			self.get_widget("button_icon_apply").set_sensitive(True)
		else:
			self.get_widget("button_icon_apply").set_sensitive(False)
		icon_switch(item)

	# hook the combo-box up to change themes
	box = self.get_widget("combobox_widget_theme")
	box.connect("changed", change_theme_cb)
	box2 = self.get_widget("combobox_icon_theme")
	box2.connect("changed", change_icons_cb)

	# hook up the apply buttons
	self.get_widget("button_widget_apply").connect("clicked", self.theme_switch_cb)
	self.get_widget("button_icon_apply").connect("clicked", self.icon_switch_cb)


   ''' Change the gtk theme globally (not just inside the theme preview '''
   def theme_switch_cb(self, wid):
	box = self.get_widget("combobox_widget_theme")
	active = box.get_active_iter()
	item = box.get_model()[active][0]
	self.gnome_settings.set_string("gtk-theme", item)
	self.get_widget("button_widget_apply").set_sensitive(False)

   ''' Change the gtk theme globally (not just inside the theme preview '''
   def icon_switch_cb(self, wid):
	box = self.get_widget("combobox_icon_theme")
	active = box.get_active_iter()
	item = box.get_model()[active][0]
	self.gnome_settings.set_string("icon-theme", item)
	self.get_widget("button_icon_apply").set_sensitive(False)

   ''' Populate the combobox with theme names '''
   def build_themes_list(self):
	homedir = os.getenv('HOME')
	xdg_dirs = [ '/usr/share/themes', '%s/.themes/' % homedir ]

	themes_model = Gtk.ListStore(str)

	for xdg_dir in xdg_dirs:
		if not os.path.exists(xdg_dir):
			continue
		# loop through the directory finding gtk3 themes
		for d in os.listdir(xdg_dir):
			name = d
			path = os.path.join(xdg_dir, d)
			gtk3hopeful = os.path.join(path, 'gtk-3.0')
			if os.path.exists(gtk3hopeful):
				themes_model.append([name])
	# now we'll put them in the combobox. so you can select em :)
	box = self.get_widget("combobox_widget_theme")
	box.set_model(themes_model)
	renderer_text = Gtk.CellRendererText()
	box.pack_start(renderer_text, True)
	box.add_attribute(renderer_text, "text", 0)

   ''' Populate the combobox with icon theme names '''
   def build_icons_list(self):
	homedir = os.getenv('HOME')
	xdg_dirs = [ '/usr/share/icons', '%s/.icons/' % homedir ]

	themes_model = Gtk.ListStore(str)

	for xdg_dir in xdg_dirs:
		if not os.path.exists(xdg_dir):
			continue
		# loop through the directory finding gtk3 themes
		for d in os.listdir(xdg_dir):
			name = d
			path = os.path.join(xdg_dir, d)
			gtk3hopeful = os.path.join(path, 'index.theme')
			if os.path.exists(gtk3hopeful):
				themes_model.append([name])
	# now we'll put them in the combobox. so you can select em :)
	box = self.get_widget("combobox_icon_theme")
	box.set_model(themes_model)
	renderer_text = Gtk.CellRendererText()
	box.pack_start(renderer_text, True)
	box.add_attribute(renderer_text, "text", 0)


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

   ''' Helper function, init a checkboxfrom GConf '''
   def init_switch_gconf(self, settings, key, widget_name):
	widget = self.get_widget(widget_name)
	value = settings.get_bool(key)
	widget.set_active(value)

	def change_switch_gconf(wid,data=None):
		settings.set_bool(key, widget.get_active())

	widget.connect("notify::active", change_switch_gconf)


	self.add_notify(key,widget)

   ''' Notify helper '''
   def add_notify(self, key, widget):
	notify_id = self.metacity_settings.notify_add(key, self.key_changed_callback, widget)
	widget.set_data('notify_id', notify_id)
	widget.set_data('client', self.metacity_settings)
	widget.connect("destroy", self.destroy_callback)

   ''' destroy the associated notifications '''
   def destroy_callback (self, widget):
	client = widget.get_data ('client')
	notify_id = widget.get_data ('notify_id')

	if notify_id:
		client.notify_remove (notify_id)

   ''' Callback for gconf. update our internal values '''
   def key_changed_callback (self, client, cnxn_id, entry, widget):
        # deal with all boolean (checkboxes)
	if(entry.value.type == GConf.ValueType.BOOL):
		value = entry.value.get_bool()
                if(widget):
                    widget.set_active(value)
	elif(entry.value.type == GConf.ValueType.STRING):
                if(not widget and not value):
                    return
		# the string in question :)
		value = entry.value.get_string()
		index=0
		for row in widget.get_model():
			if(value == row[1]):
				widget.set_active(index)
				break
			index = index +1


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
   def init_combobox(self, settings, key, widget_name, abnormal=False):
	widget = self.get_widget(widget_name)
	value = settings.get_string(key)

	model = widget.get_model()

	# somethin' changed!
	def the_combo_cb(sets,key):
		value_new = sets.get_string(key)
		row=0
		for i in model:
			row+=1
			testee = i[0]
			if abnormal:
				testee = i[1]

			if value == testee:
				widget.set_active(row)
				break

	def go_change_combo(wid,data=None):
		selected = widget.get_active_iter()
		if selected is not None:
			value = model[selected][1]
			settings.set_string(key, value)

	row = 0
	# set the row to the currently used setting
	for i in model:
		testee = i[0]
		if abnormal:
			testee = i[1]
		if value == testee:
			widget.set_active(row)
			break
		row+=1
	settings.connect("changed::%s" % key, the_combo_cb)
	if abnormal:
		widget.connect("changed", go_change_combo)

   ''' Helper function, initialises a combobox to a gconf value and binds it '''
   def init_gconf_combobox(self, settings, key, widget_name, abnormal=False):
	widget = self.get_widget(widget_name)
	value = settings.get_string(key)

	model = widget.get_model()

	# somethin' changed!
	def the_combo_cb(sets,key):
		value_new = sets.get_string(key)
		row=0
		for i in model:
			row+=1
			testee = i[0]
			if abnormal:
				testee = i[1]

			if value == testee:
				widget.set_active(row)
				break

	def go_change_combo(wid,data=None):
		selected = widget.get_active_iter()
		if selected is not None:
			value = model[selected][1]
			settings.set_string(key, value)

	row = 0
	# set the row to the currently used setting
	for i in model:
		testee = i[0]
		if abnormal:
			testee = i[1]
		if value == testee:
			widget.set_active(row)
			break
		row+=1
	self.add_notify(key,widget)
	if abnormal:
		widget.connect("changed", go_change_combo)

########
# MAIN #
########
if __name__ == "__main__":

	win = AppearanceWindow()

	Gtk.main()

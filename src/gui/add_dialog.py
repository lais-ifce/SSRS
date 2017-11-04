import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class AddDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Add mount point", parent, 0, (Gtk.STOCK_ADD, Gtk.ResponseType.ACCEPT,
                                                                 Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.parent = parent
        self.set_default_size(420, 180)
        self.box = self.get_content_area()
        self.box_inside = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # remote input
        self.entry_remote = Gtk.Entry()
        self.box_inside.pack_start(Gtk.Label("Remote Location"), True, True, 0)
        self.box_inside.pack_start(self.entry_remote, True, False, 0)
        # local input
        self.box_local = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.entry_local = Gtk.Entry()
        self.button_local = Gtk.Button(stock=Gtk.STOCK_OPEN)
        self.button_local.connect("clicked", self.file_chooser)
        self.box_local.pack_start(self.entry_local, True, True, 0)
        self.box_local.pack_start(self.button_local, False, False, 0)
        self.box_inside.pack_start(Gtk.Label("Local Path"), True, True, 0)
        self.box_inside.pack_start(self.box_local, True, False, 0)
        self.box.pack_start(self.box_inside, True, True, 0)
        # setup dialog
        self.connect("response", self.eval_response)
        self.show_all()
        self.run()

    def eval_response(self, *args):
        if args[1] == Gtk.ResponseType.ACCEPT:
            if self.entry_local.get_text() != "" and self.entry_remote.get_text() != "":
                self.parent.mount_store.append([self.entry_local.get_text(), self.entry_remote.get_text(), "No"])
                self.parent.mount_points.append({
                    "local_path": self.entry_local.get_text(),
                    "remote_path": self.entry_remote.get_text()
                })
        self.destroy()

    def file_chooser(self, *args):
        dialog = Gtk.FileChooserDialog("Choose a folder", self, Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entry_local.set_text(dialog.get_filename())
        dialog.destroy()

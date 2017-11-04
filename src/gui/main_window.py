import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from src.gui.search_dialog import SearchDialog
from src.gui.add_dialog import AddDialog
from src.gui.Manage import Manage
from src.config import *
import pickle
import os


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.ApplicationWindow.__init__(self, title="SRSS")
        # setup window
        self.set_default_size(800, 600)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)
        # setup box and tree view
        self.inside_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.scrl = Gtk.ScrolledWindow()
        self.scrl.set_vexpand(True)
        self.mount_store = Gtk.ListStore(str, str, str)
        self.tree_view = Gtk.TreeView(self.mount_store)
        self.tree_view.append_column(Gtk.TreeViewColumn("Local Path", Gtk.CellRendererText(), text=0))
        self.tree_view.append_column(Gtk.TreeViewColumn("Remote Path", Gtk.CellRendererText(), text=1))
        self.tree_view.append_column(Gtk.TreeViewColumn("Mounted", Gtk.CellRendererText(), text=2))
        self.scrl.add(self.tree_view)
        # setup side buttons
        self.side_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.button_add = Gtk.Button(stock=Gtk.STOCK_ADD)
        self.button_add.connect("clicked", self.action_add)
        self.button_rem = Gtk.Button(stock=Gtk.STOCK_REMOVE)
        self.button_rem.connect("clicked", self.action_rem)
        self.button_mount = Gtk.Button(label="Mount")
        self.button_mount.connect("clicked", self.action_mount)
        self.button_unmount = Gtk.Button(label="Unmount")
        self.button_unmount.connect("clicked", self.action_unmount)
        self.button_search = Gtk.Button(stock=Gtk.STOCK_FIND)
        self.button_search.connect("clicked", self.action_search)
        self.button_sync = Gtk.Button(label="SYNC")
        self.button_sync.connect("clicked", self.action_sync)
        # add side buttons to side box
        self.side_box.pack_start(self.button_add, False, False, 0)
        self.side_box.pack_start(self.button_rem, False, False, 0)
        self.side_box.pack_start(Gtk.Separator(), False, False, 0)
        self.side_box.pack_start(self.button_mount, False, False, 0)
        self.side_box.pack_start(self.button_unmount, False, False, 0)
        self.side_box.pack_start(Gtk.Separator(), False, True, 0)
        self.side_box.pack_start(self.button_sync, False, False, 0)
        self.side_box.pack_start(Gtk.Separator(), True, True, 0)
        self.side_box.pack_start(self.button_search, False, False, 0)
        # add secondary boxes to main
        self.inside_box.pack_start(self.scrl, True, True, 0)
        self.inside_box.pack_start(self.side_box, False, False, 0)
        self.box.pack_start(self.inside_box, True, True, 0)

        self.mounted_fs = Manage()
        if os.path.exists(MOUNT_POINT_FILE):
            with open(MOUNT_POINT_FILE, "rb") as f:
                self.mount_points = pickle.load(f)
                for i in self.mount_points:
                    self.mount_store.append([i['local_path'], i['remote_path'], "No"])
        else:
            self.mount_points = []

    def action_add(self, widget):
        AddDialog(self)

    def action_rem(self, widget):
        selected = self.tree_view.get_selection().get_selected()
        if self.confirm(self, "You really want remove this mount point?") and selected[1] is not None:
            for i in range(0, len(self.mount_points)):
                if self.mount_points[i]['local_path'] == self.mount_store.get_value(selected[1], 0):
                    del self.mount_points[i]
            self.mount_store.remove(selected[1])

    def action_mount(self, widget):
        selected = self.tree_view.get_selection().get_selected()
        senha = self.get_password(self)
        local = self.mount_store.get_value(selected[1], 0)
        remote = self.mount_store.get_value(selected[1], 1)
        if senha != "":
            if self.mounted_fs.add_mount_point(local, remote, senha):
                self.mount_store.set_value(selected[1], 2, "Yes")

    def action_unmount(self, widget):
        selected = self.tree_view.get_selection().get_selected()
        if self.mounted_fs.rem_mount_point(self.mount_store.get_value(selected[1], 0)):
            self.mount_store.set_value(selected[1], 2, "No")

    def action_search(self, widget):
        SearchDialog(self)

    def action_sync(self, widget):
        selected = self.tree_view.get_selection().get_selected()
        self.confirm(self, "Sincronizado")

    @staticmethod
    def get_password(parent):
        dialog = Gtk.Dialog("Password", parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        box = dialog.get_content_area()
        entry = Gtk.Entry()
        entry.set_visibility(False)
        box.pack_start(Gtk.Label("Password"), True, False, 0)
        box.pack_start(entry, True, True, 0)
        dialog.show_all()
        response = dialog.run()
        value = ""
        if response == Gtk.ResponseType.OK:
            value = entry.get_text()
        dialog.destroy()
        return value

    @staticmethod
    def confirm(parent, message):
        dialog = Gtk.Dialog("Confirmation", parent, 0, (Gtk.STOCK_YES, Gtk.ResponseType.YES,
                                                        Gtk.STOCK_NO, Gtk.ResponseType.NO))
        box = dialog.get_content_area()
        box.pack_start(Gtk.Label(message), True, True, 0)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            return True
        return False

    def quit(self, *args):
        self.mounted_fs.destroy()
        if not os.path.exists(CONFIG_FOLDER):
            os.mkdir(CONFIG_FOLDER)
        with open(MOUNT_POINT_FILE, "wb") as f:
            pickle.dump(self.mount_points, f)
        Gtk.main_quit(args)


if __name__ == "__main__":
    main = MainWindow()
    main.connect("delete-event", main.quit)
    main.show_all()
    Gtk.main()

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
    """
    Class that extends Gtk application windows and is the base window
    """
    def __init__(self):
        """
        Constructor
        """
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
        """
        Action to add a mount point
        :param widget: Gtk Widget
        :return: None
        """
        AddDialog(self)

    def action_rem(self, widget):
        """
        Action to remove an mount point
        :param widget: Gtk widget
        :return: None
        """
        selected = self.tree_view.get_selection().get_selected()
        if self.confirm(self, "You really want remove this mount point?") and selected[1] is not None:
            for i in range(0, len(self.mount_points)):
                if self.mount_points[i]['local_path'] == self.mount_store.get_value(selected[1], 0):
                    del self.mount_points[i]
            self.mount_store.remove(selected[1])

    def action_mount(self, widget):
        """
        Mount a previously added mount point
        :param widget: Gtk widget
        :return: None
        """
        selected = self.tree_view.get_selection().get_selected()
        senha = self.get_password(self)
        local = self.mount_store.get_value(selected[1], 0)
        remote = self.mount_store.get_value(selected[1], 1)
        if senha != "":
            result, message = self.mounted_fs.mount(local, remote, senha)
            if result is True:
                self.mount_store.set_value(selected[1], 2, "Yes")
            else:
                self.info(self, message)

    def action_unmount(self, widget):
        """
        Unmount a previously mounted mount point
        :param widget: Gtk Widget
        :return: None
        """
        selected = self.tree_view.get_selection().get_selected()
        if self.mounted_fs.unmount(self.mount_store.get_value(selected[1], 0)):
            self.mount_store.set_value(selected[1], 2, "No")

    def action_search(self, widget):
        """
        Trig the search dialog for all mounted mount points
        :param widget: Gtk Widget
        :return: None
        """
        SearchDialog(self)

    def action_sync(self, widget):
        """
        Trig the sync task for the selected mount point
        :param widget:
        :return:
        """
        selected = self.tree_view.get_selection().get_selected()
        if self.confirm(self, "Really want sync this repository?"):
            local = self.mount_store.get_value(selected[1], 0)
            remote = self.mount_store.get_value(selected[1], 1)
            self.mounted_fs.start_sync(local, remote)

    @staticmethod
    def get_password(parent):
        """
        Dialog to ask for a password
        :param parent: Gtk parent window
        :return: password or empty string
        """
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
        """
        Confirmation dialog
        :param parent: Gtk parent window
        :param message: message to be showed
        :return: True or False
        """
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

    @staticmethod
    def info(parent, message):
        """
        Information dialog
        :param parent: Gtk parent window
        :param message: info message to be showed
        :return: None
        """
        dialog = Gtk.Dialog("Information", parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        box = dialog.get_content_area()
        box.pack_start(Gtk.Label(message), True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def quit(self, *args):
        """
        Perform operations to safe exit
        :param args: Gtk args
        :return: None
        """
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

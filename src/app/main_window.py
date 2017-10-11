import os
import gi
from src.app.search_dialog import SearchDialog
from src.app.mount_dialog import MountDialog
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MainWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(os.path.dirname(__file__), "glade/main_window.glade"))
        self.main = self.builder.get_object("main_window")
        self.main.show_all()
        self.search = SearchDialog(self.builder)
        self.mount = MountDialog(self.builder)
        self.handlers = {
            "on_main_window_destroy": self.on_main_window_destroy,
            "on_btn_add_mount_clicked": self.launch_add_mount_point,
            "on_btn_remove_mount_clicked": self.launch_remove_mount_point,
            "on_btn_mount_clicked": self.mount_point,
            "on_btn_unmount_clicked": self.unmount_point,
            "on_btn_launch_find_clicked": self.launch_search_dialog,
        }
        tree = self.builder.get_object("tree_view_mount_point")
        render = Gtk.CellRendererText()
        i = 0
        for c in tree.get_columns():
            c.pack_start(render, False)
            c.add_attribute(render, "text", i)
            i += 1
        self.connect_handlers()
        Gtk.main()

    def connect_handlers(self):
        handlers = [self.handlers, self.search.handlers, self.mount.handlers]
        tmp = {}
        for h in handlers:
            for i in h.items():
                tmp[i[0]] = i[1]
        self.builder.connect_signals(tmp)

    @staticmethod
    def on_main_window_destroy(*args):
        Gtk.main_quit(*args)

    def launch_add_mount_point(self, widget):
        self.mount.run()

    def launch_remove_mount_point(self, widget):
        pass

    def mount_point(self, widget):
        pass

    def unmount_point(self, widget):
        pass

    def launch_search_dialog(self, widget):
        self.search.run()


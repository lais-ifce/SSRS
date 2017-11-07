from src.index.tools import *
from src.config import *
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import json
from requests import post


class SearchDialog(Gtk.Dialog):
    def __init__(self, parent):
        self.parent = parent
        Gtk.Dialog.__init__(self, "Find", parent, 0, (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                                      Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
        self.set_default_size(420, 250)
        self.box = self.get_content_area()
        self.box_inside = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # setup search bar
        self.box_search = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.entry_search = Gtk.SearchEntry()
        self.entry_search.connect("key-release-event", self.eval_key)
        self.button_search = Gtk.Button(stock=Gtk.STOCK_FIND)
        self.button_search.connect("clicked", self.run_search)
        self.box_search.pack_start(self.entry_search, True, True, 0)
        self.box_search.pack_start(self.button_search, False, False, 0)
        self.box_inside.pack_start(self.box_search, False, False, 0)
        # setup scrolled window and tree view
        self.scrl = Gtk.ScrolledWindow()
        self.scrl.set_vexpand(True)
        self.scrl.connect("key-release-event", self.eval_key)
        self.store_search = Gtk.ListStore(str, str)
        self.tree_view = Gtk.TreeView(self.store_search)
        self.tree_view.append_column(Gtk.TreeViewColumn("File", Gtk.CellRendererText(), text=0))
        self.tree_view.append_column(Gtk.TreeViewColumn("Path", Gtk.CellRendererText(), text=1))
        self.scrl.add(self.tree_view)
        self.box_inside.pack_start(self.scrl, True, True, 0)
        # setup dialog
        self.box.add(self.box_inside)
        self.connect("response", self.eval_response)
        self.show_all()
        self.run()

    def eval_response(self, *args):
        if args[1] == Gtk.ResponseType.ACCEPT:
            selection = self.tree_view.get_selection().get_selected()
            path = self.store_search.get_value(selection[1], 1)
            subprocess.run(["xdg-open", path])
        else:
            self.destroy()

    def eval_key(self, *args):
        if type(args[0]) is gi.repository.Gtk.SearchEntry and args[1].keyval == Gdk.KEY_Return:
            self.run_search()
        elif type(args[0]) is gi.repository.Gtk.ScrolledWindow and args[1].keyval == Gdk.KEY_Return:
            self.eval_response("", Gtk.ResponseType.ACCEPT)

    def run_search(self, *args):
        self.store_search.clear()
        mounted = self.parent.mounted_fs.mounted
        for path in mounted.keys():
            key = mounted[path]['key']
            terms = self.entry_search.get_text().split(" ")
            terms = [x.decode('utf-8') for x in hash_terms(filter_stop(normalize(terms)), key)]
            url = mounted[path]['remote'] + '/' if mounted[path]['remote'][-1] != '/' else mounted[path]['remote']
            r = post(url + 'search', data=json.dumps({'data': terms}),
                     headers={"Content-type": "application/json"})
            if "ok" in r.json().keys() and r.json()['ok']:
                for item in r.json()['data']:
                    self.store_search.append([item.split("/")[-1], item])

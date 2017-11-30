import json
import subprocess

import gi
from requests import post

from client.index.tools import *
from config import CONFIG_FOLDER

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class SearchDialog(Gtk.Dialog):
    """
    Class that extends Gtk.Dialog and is used to manage user's queries and their answers
    """
    def __init__(self, parent):
        """
        Constructor
        :param parent: Gtk parent window
        """
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
        """
        Evaluate the dialog response and when it is `ACCEPT` the selected file is opened with the xdg
        default application
        :param args: Gtk args
        :return: None
        """
        if args[1] == Gtk.ResponseType.ACCEPT:
            selection = self.tree_view.get_selection().get_selected()
            path = self.store_search.get_value(selection[1], 1)
            subprocess.run(["xdg-open", path])
        else:
            self.destroy()

    def eval_key(self, *args):
        """
        Evaluate pressed keys and trig the related action
        :param args: Gtk args
        :return: None
        """
        if type(args[0]) is gi.repository.Gtk.SearchEntry and args[1].keyval == Gdk.KEY_Return:
            self.run_search()
        elif type(args[0]) is gi.repository.Gtk.ScrolledWindow and args[1].keyval == Gdk.KEY_Return:
            self.eval_response("", Gtk.ResponseType.ACCEPT)

    def run_search(self, *args):
        """
        Perform a remote search with the terms entered on the search box on all mounted file systems and put the
        results on the tree view
        :param args: Gtk args
        :return: None
        """
        self.store_search.clear()
        mounted = self.parent.mounted_fs.mounted
        for path in mounted.keys():
            key = mounted[path]['key']
            terms = self.entry_search.get_text().split(" ")
            terms = [x.decode('utf-8') for x in hash_terms(filter_stop(normalize(terms)), key)]
            r = post(mounted[path]['remote'] + '/search', data=json.dumps({'data': terms}),
                     headers={"Content-type": "application/json"}, verify=CONFIG_FOLDER+'/trusted')
            if "ok" in r.json().keys() and r.json()['ok']:
                for cipher in r.json()['data']:
                    mounted[path]['cmd'].put((3, cipher))
                    item = mounted[path]['q'].get().split('/')[-1]
                    self.store_search.append([item, os.path.join(mounted[path]['path'], item)])

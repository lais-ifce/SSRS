from src.index.QueryFilter import QueryFilter
from src.index import tools
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class SearchDialog:
    def __init__(self, *builder):
        self.builder = builder[0]
        self.search = self.builder.get_object("search_dialog")
        self.handlers = {
            "on_btn_run_search_clicked": self.run_search
        }
        tree = self.builder.get_object("tree_view_search")
        render = Gtk.CellRendererText()
        i = 0
        for c in tree.get_columns():
            c.pack_start(render, False)
            c.add_attribute(render, "text", i)
            i += 1
        self.search.connect("response", self.get_response)

    def get_response(self, widget, response):
        if response == 1:
            select = self.builder.get_object("selection_search").get_selected()
            rlist = self.builder.get_object("store_search")
            path = rlist.get_value(select[1], 1)
            subprocess.run(["xdg-open", path])
        else:
            self.search.destroy()

    def run_search(self, widget):
        data = tools.hash_terms(tools.filter_stop(tools.normalize(self.builder.get_object("entry_run_search")
                                                                  .get_text().split(" "))), "MYKEY")
        qf = QueryFilter(data, "/home/wsantos/MEGAsync/Books/.index/")
        result = qf.run_query()
        if len(result) > 0:
            rlist = self.builder.get_object("store_search")
            rlist.clear()
            for i in result[0]:
                j = (i[1].split("/")[-1], i[1])
                rlist.append(j)
            tree = self.builder.get_object("tree_view_search")
            tree.set_model(rlist)


    def run(self):
        self.search.run()

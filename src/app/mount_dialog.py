class MountDialog:
    def __init__(self, *builder):
        self.builder = builder[0]
        self.mount = self.builder.get_object("add_mount_dialog")
        self.handlers = {
            "on_btn_launch_folder_mount_clicked": self.launch_folder_choose
        }
        self.choose = self.builder.get_object("folder_choose_dialog")
        self.mount.connect("response", self.get_response)

    def get_response(self, widget, response):
        if response == 1:
            remote = self.builder.get_object("entry_mount_remote").get_text()
            local = self.builder.get_object("entry_mount_local").get_text()
            print(remote, local)
        else:
            pass
        self.mount.destroy()

    def launch_folder_choose(self, widget):
        self.choose.connect("response", self.get_folder_choose_response)
        self.choose.run()

    def get_folder_choose_response(self, widget, response):
        if response == 1:
            self.builder.get_object("entry_mount_local").set_text(self.choose.get_filename())
        else:
            pass
        self.choose.destroy()

    def run(self):
        self.mount.run()

from os import path

DEBUG = True

CONFIG_FOLDER = path.expanduser("~/.config/ssrs")

MOUNT_POINT_FILE = path.join(CONFIG_FOLDER, "mount.point")

SERVER_PORT = 8080

SERVER_IP = '127.0.0.1'

INDEX_ROOT = path.join(CONFIG_FOLDER, "index")

PROTOCOL = "http://"

BASE_URL = PROTOCOL + SERVER_IP + ":" + str(SERVER_PORT)

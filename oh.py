# -*- coding: utf-8 -*-
import weechat, random

# requires prism.py

SCRIPT_NAME    = "oh"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "react appropriately"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

def oh_cb(data, buffer, args):
    oh = 'O' * random.randint(20,50) + 'H'
    weechat.command(buffer, "/p {}".format(oh))
    return weechat.WEECHAT_RC_OK

hook = weechat.hook_command("oh", "react appropriately",
    "",
    "",
    "",
    "oh_cb", "")

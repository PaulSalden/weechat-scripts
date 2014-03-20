# -*- coding: utf-8 -*-
import weechat

SCRIPT_NAME    = "qinvite"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "0.0.1"
SCRIPT_LICENSE = "WTFOMGBBQ"
SCRIPT_DESC    = "auto-join on Q invite"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
              SCRIPT_LICENSE, SCRIPT_DESC, "", "")

_OK = weechat.WEECHAT_RC_OK

def _server_buffer(server):
    return weechat.buffer_search("irc", "server.{}".format(server))

def invite_cb(data, signal, signal_data):
    server = signal.split(",")[0]
    args = signal_data.split()
    fullhost = args[0][1:]
    if fullhost == "Q!TheQBot@CServe.quakenet.org":
    	channel = args[3]
    	weechat.command(_server_buffer(server), "/join {}".format(channel))
    return _OK

weechat.hook_signal("*,irc_in2_invite", "invite_cb", "")
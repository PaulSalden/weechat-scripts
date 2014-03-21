# -*- coding: utf-8 -*-
import weechat

SCRIPT_NAME    = "qinvite"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "2.0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "auto-join on Q invite"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

_OK = weechat.WEECHAT_RC_OK

def _server_buffer(server):
    return weechat.buffer_search("irc", "server.{}".format(server))

queue = {}

def add_invite(server, channel):
    servbuf = _server_buffer(server)
    if servbuf not in queue:
        queue[servbuf] = [channel]
        weechat.hook_timer(1000, 0, 1, "timer_cb", servbuf)
    else:
        queue[servbuf].append(channel)

def timer_cb(servbuf, remaining_calls):
    channels = queue.pop(servbuf)
    while channels:
        chanstring = ",".join(channels[:10])
        weechat.command(servbuf, "/join {}".format(chanstring))
        channels = channels[10:]
    return _OK

def invite_cb(data, signal, signal_data):
    server = signal.split(",")[0]
    args = signal_data.split()
    fullhost = args[0][1:]
    if fullhost == "Q!TheQBot@CServe.quakenet.org":
        channel = args[3]
        add_invite(server, channel)
    return _OK

weechat.hook_signal("*,irc_in2_invite", "invite_cb", "")

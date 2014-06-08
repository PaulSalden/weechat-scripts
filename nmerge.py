# -*- coding: utf-8 -*-
import weechat

SCRIPT_NAME    = "nmerge"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "merge newserv instance queries"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

def _newserv_match(name):
    return name[0] == "N" and (len(name) == 1 or name[1:].isdigit())

def _find_first_buffer_number():
    infolist = weechat.infolist_get('buffer', '', '')
    while weechat.infolist_next(infolist):
        short_name = weechat.infolist_string(infolist, 'short_name')
        if _newserv_match(short_name):
            number = weechat.infolist_integer(infolist, 'number')
            return number

def private_opened_cb(data, signal, signal_data):
    buffer = signal_data
    short_name = weechat.buffer_get_string(buffer, "short_name")
    if _newserv_match(short_name):
        destination = _find_first_buffer_number()
        weechat.command(buffer, "/buffer merge {}".format(destination))
    return weechat.WEECHAT_RC_OK

weechat.hook_signal('irc_pv_opened', 'private_opened_cb', '')

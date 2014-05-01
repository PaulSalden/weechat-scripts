# -*- coding: utf-8 -*-
import weechat

SCRIPT_NAME    = "check"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "parse /check output"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

checkbuffer = ""
serverbuffer = ""

def check_buffer_input_cb(data, buffer, input_data):
    weechat.command(serverbuffer, "/quote check {}".format(input_data))
    return weechat.WEECHAT_RC_OK

def check_buffer_close_cb(data, buffer):
    global checkbuffer, serverbuffer
    checkbuffer = ""
    serverbuffer = ""
    return weechat.WEECHAT_RC_OK

def check_modifier_cb(data, modifier, modifier_data, string):
    global checkbuffer, serverbuffer
    if not checkbuffer:
        checkbuffer = weechat.buffer_new("check", "check_buffer_input_cb", "",
            "check_buffer_close_cb", "")
    if serverbuffer != modifier_data:
        serverbuffer = weechat.buffer_search("irc", "server.{}".format(modifier_data))
        weechat.buffer_set(checkbuffer, "title", "CHECK output (server: {})".format(modifier_data))
    if modifier == "irc_in_286":
        line = weechat.color("chat_prefix_join") + string.split(":", 2)[2]
    else:
        line = string.split(":", 2)[2]
    weechat.prnt(checkbuffer, line)
    return ""

for raw in (286, 287, 290, 291, 408, 461, 481):
    weechat.hook_modifier("irc_in_"+str(raw), "check_modifier_cb", "")

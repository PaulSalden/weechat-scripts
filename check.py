# -*- coding: utf-8 -*-
import weechat

SCRIPT_NAME    = "check"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "0.0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "parse /check output"

# TODO: allow easy /check'ing from check buffer

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

checkbuffer = ""

def check_buffer_close_cb(data, buffer):
    global checkbuffer
    checkbuffer = ""
    return weechat.WEECHAT_RC_OK

def check_modifier_cb(data, modifier, modifier_data, string):
    global checkbuffer
    if not checkbuffer:
        checkbuffer = weechat.buffer_new("check", "", "", "check_buffer_close_cb", "")
        weechat.buffer_set(checkbuffer, "title", "CHECK output")
    if modifier == "irc_in_286":
        line = weechat.color("chat_prefix_join") + string.split(":", 2)[2]
    else:
        line = string.split(":", 2)[2]
    weechat.prnt(checkbuffer, line)
    return ""

for raw in (286, 287, 290, 291, 408, 461, 481):
    weechat.hook_modifier("irc_in_"+str(raw), "check_modifier_cb", "")

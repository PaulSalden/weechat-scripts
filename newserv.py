# -*- coding: utf-8 -*-
import weechat

SCRIPT_NAME    = "newserv"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "print newserv instance notices in a dedicated buffer"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

# adjust to fit weechat setup
NETWORK = "quakenet"

def _newserv_match(nick):
    return nick[0] == "N" and (len(nick) == 1 or nick[1:].isdigit())

nsbuffer = ""
def open_newserv_buffer():
    global nsbuffer
    if not nsbuffer:
        nsbuffer = weechat.buffer_new("newserv", "newserv_buffer_input_cb", "", "newserv_buffer_close_cb", "")
        weechat.buffer_set(nsbuffer, "title", "newserv - input will be sent as /msg on {}!".format(NETWORK))

serverbuffer = weechat.buffer_search("irc", "server.{}".format(NETWORK))
def newserv_buffer_input_cb(data, buffer, input_data):
    weechat.command(serverbuffer, "/msg {}".format(input_data))
    return weechat.WEECHAT_RC_OK

def newserv_buffer_close_cb(data, buffer):
    global nsbuffer
    nsbuffer = ""
    return weechat.WEECHAT_RC_OK

def modifier_cb(data, modifier, modifier_data, string):
    global nsbuffer
    input = weechat.info_get_hashtable("irc_message_parse", { "message": string })
    if modifier_data == NETWORK and _newserv_match(input["nick"]):
        if not nsbuffer:
            open_newserv_buffer()

        ncolor = weechat.info_get("irc_nick_color_name", input["nick"])
        weechat.prnt(nsbuffer, "{}{}{}\t{}".format(weechat.color(ncolor), input["nick"], weechat.color("reset"), input["text"]))
        return ""
    return string

weechat.hook_modifier("irc_in_notice", "modifier_cb", "")

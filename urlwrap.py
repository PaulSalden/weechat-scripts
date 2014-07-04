# -*- coding: utf-8 -*-
import weechat
from time import strftime

SCRIPT_NAME    = "urlwrap"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org"
SCRIPT_VERSION = "0.9"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Prevents alignment of multiline messages containing an url."

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "shutdown_cb", "")

weechat.command("", "/filter add urlwrap_filter * urlwrap_filter_tag *")

def _get_buffer(server, channel):
    return weechat.info_get("irc_buffer", ",".join((server, channel)))

def _s(option):
    # return the string value of option
    return weechat.config_string(weechat.config_get(option))

def _c(option):
    # return a color character with number based on option
    return weechat.color(weechat.config_color(weechat.config_get(option)))

def _reconstruct_print(string):
    # as printing without alignment also strips timestamp and delimiter,
    # they must be reconstructed
    timestamp = strftime(_s("weechat.look.buffer_time_format"))
    timestamp = _c("weechat.color.chat_time") + "".join([
        l if l.isdigit() else _c("weechat.color.chat_time_delimiters")+l+_c("weechat.color.chat_time")
        for l in timestamp])

    delimiter = " {} {}".format(_c("weechat.color.chat_delimiters") + _s("weechat.look.prefix_suffix"),
        weechat.color("reset"))
    string = string.replace("\t", delimiter)

    return "{} {}".format(timestamp, string)

def modifier_cb(data, modifier, modifier_data, string):
    if "http://" in string or "https://" in string:
        buffer = weechat.buffer_search("irc", modifier_data.split(";")[1])
        weechat.prnt_date_tags(buffer, 0, "urlwrap_filter_tag", string)
        weechat.prnt(buffer, "\t\t{}".format(_reconstruct_print(string)))
        return ""
    return string

def shutdown_cb():
    weechat.command("", "/del filter urlwrap_filter")
    return weechat.WEECHAT_RC_OK

weechat.hook_modifier("weechat_print", "modifier_cb", "")

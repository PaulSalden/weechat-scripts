# -*- coding: utf-8 -*-
import weechat
from time import strftime

SCRIPT_NAME    = "urlwrap"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "0.95"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Prevents alignment of multiline messages containing an url."

# This script utilizes filter '_urlwrap_filter'. Do not load if you are somehow
# manually using it.

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "shutdown_cb", "")

weechat.command("", "/filter add _urlwrap_filter * urlwrap_filter_tag *")

def _get_buffer(server, channel):
    return weechat.info_get("irc_buffer", ",".join((server, channel)))

def _s(option):
    # return the string value of option
    return weechat.config_string(weechat.config_get(option))

def _c(option, bgoption=False):
    # return a color character with numbers based on options
    if bgoption:
        return weechat.color(",".join((weechat.config_color(weechat.config_get(option)),
            weechat.config_color(weechat.config_get(bgoption)))))
    return weechat.color(weechat.config_color(weechat.config_get(option)))

def _reconstruct_print(string, highlighted):
    # as printing without alignment also strips timestamp and delimiter,
    # they must be reconstructed
    timestamp = strftime(_s("weechat.look.buffer_time_format"))
    timestamp = _c("weechat.color.chat_time") + "".join([
        l if l.isdigit() else _c("weechat.color.chat_time_delimiters")+l+_c("weechat.color.chat_time")
        for l in timestamp])

    nick, message = string.split("\t", 1)
    if highlighted:
        nick = "".join((_c("weechat.color.chat_highlight", "weechat.color.chat_highlight_bg"),
            weechat.string_remove_color(nick, "")))
    nick = "".join((_c("weechat.color.chat_nick_prefix"), _s("weechat.look.nick_prefix"),
        nick, _c("weechat.color.chat_nick_suffix"), _s("weechat.look.nick_suffix"),
        weechat.color("reset")))

    delimiter = "".join((" ", _c("weechat.color.chat_delimiters"), _s("weechat.look.prefix_suffix"),
        weechat.color("reset"), " ")) if _s("weechat.look.prefix_align") != "none" else " "

    return "{} {}{}{}".format(timestamp, nick, delimiter, message)

def modifier_cb(data, modifier, modifier_data, string):
    if "irc_privmsg" in modifier_data and ("http://" in string or "https://" in string):
        buffer = weechat.buffer_search("irc", modifier_data.split(";")[1])
        nick = weechat.buffer_get_string(buffer, "localvar_nick")
        highlighted = nick in string
        weechat.prnt_date_tags(buffer, 0, "urlwrap_filter_tag", string)
        weechat.prnt(buffer, "\t\t{}".format(_reconstruct_print(string, highlighted)))
        return ""
    return string

def shutdown_cb():
    weechat.command("", "/filter del _urlwrap_filter")
    return weechat.WEECHAT_RC_OK

weechat.hook_modifier("weechat_print", "modifier_cb", "")

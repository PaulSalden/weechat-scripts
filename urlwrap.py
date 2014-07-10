# -*- coding: utf-8 -*-
import weechat
from time import strftime

SCRIPT_NAME    = "urlwrap"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "0.99"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Prevents alignment of multiline messages containing an url."

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "shutdown_cb", "")

infolist = weechat.infolist_get("filter", "", "")
filters = []
while weechat.infolist_next(infolist):
        filters.append(weechat.infolist_string(infolist, "name"))
weechat.infolist_free(infolist)

filtername = "urlwrap_filter"
while filtername in filters: filtername = "".join((filtername, "_"))

weechat.command("", "/filter add {} * urlwrap_filter_tag *".format(filtername))

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

def _reconstruct_print(prefix, message, highlighted):
    # as printing without alignment also strips timestamp and delimiter,
    # they must be reconstructed
    timestamp = strftime(_s("weechat.look.buffer_time_format"))
    timestamp = _c("weechat.color.chat_time") + "".join([
        l if l.isdigit() else _c("weechat.color.chat_time_delimiters")+l+_c("weechat.color.chat_time")
        for l in timestamp])

    if highlighted:
        prefix = "".join((_c("weechat.color.chat_highlight", "weechat.color.chat_highlight_bg"),
            weechat.string_remove_color(prefix, "")))
    prefix = "".join((_c("weechat.color.chat_nick_prefix"), _s("weechat.look.nick_prefix"),
        prefix, _c("weechat.color.chat_nick_suffix"), _s("weechat.look.nick_suffix"),
        weechat.color("reset")))

    delimiter = "".join((" ", _c("weechat.color.chat_delimiters"), _s("weechat.look.prefix_suffix"),
        weechat.color("reset"), " ")) if _s("weechat.look.prefix_align") != "none" else " "

    return "{} {}{}{}".format(timestamp, prefix, delimiter, message)

def modifier_cb(data, modifier, modifier_data, string):
    if "irc_privmsg" in modifier_data and ("http://" in string or "https://" in string):
        buffer = weechat.buffer_search("irc", modifier_data.split(";")[1])
        mynick = weechat.buffer_get_string(buffer, "localvar_nick")

        taglist = modifier_data.split(";")[2].split(",")
        for tag in taglist:
            if tag[:5] == "nick_":
                nick = tag[5:]
                break

        prefix, message = string.split("\t", 1)

        highlighted = nick != mynick and weechat.string_has_highlight(message, mynick)
        weechat.prnt_date_tags(buffer, 0, "urlwrap_filter_tag", string)
        weechat.prnt(buffer, "\t\t{}".format(_reconstruct_print(prefix, message, highlighted)))
        return ""
    return string

def shutdown_cb():
    weechat.command("", "/filter del {}".format(filtername))
    return weechat.WEECHAT_RC_OK

weechat.hook_modifier("weechat_print", "modifier_cb", "")

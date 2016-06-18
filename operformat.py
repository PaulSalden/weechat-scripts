# -*- coding: utf-8 -*-
import weechat, re

SCRIPT_NAME    = "operformat"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "reformat service and server notices to make them more readable"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

# for readability
def c(color):
    return weechat.color(color)
def nc(nick):
    #return weechat.color(weechat.info_get("nick_color", nick))
    return weechat.info_get("nick_color", nick)

# adjust to preference
SERVICE = "^N[1-9]?$"
SERVER = "\.quakenet\.org$"
SERVICEPATTERNS = [
]
SERVERPATTERNS = [
    ("^[^ ]+ \*\*\* Notice -- ([^ ]+) adding global GLINE for ([^ ,]+), expiring at ([0-9]+): (.+)$",
        nc("GLINE")+"GLINE"+c("reset")+"\t{1} ({0}) {2} ("+c("irc.color.reason_quit")+"{3}"+c("reset")+")"),

    ("^[^ ]+ \*\*\* Notice -- Received KILL message for ([^ ]+)\. From ([^ ]+) Path: [^ ]+ \((.+)\)$",
        nc("KILL")+"KILL"+c("reset")+"\t{0} ({1}) ("+c("irc.color.reason_quit")+"{2}"+c("reset")+")"),

    ("^[^ ]+ \*\*\* Notice -- G-line active for (.*)\[(.*)@(.+)\]$",
        nc("G:ACTIVE")+"G:ACTIVE"+c("reset")+"\t{0}!{1}@{2}")
]

def modifier_cb(data, modifier, modifier_data, string):
    plugin, bufname, tags = modifier_data.split(";")
    tags = tags.split(",")

    # find nick
    nick = ""
    for tag in tags:
        if tag[:5] == "nick_":
            nick = tag[5:]
            break
    if not nick:
        return string

    # handle service notices
    if re.search(SERVICE, nick):
        # remove color and excess whitespace
        sstring = " ".join(weechat.string_remove_color(string, "").split())

        for pattern, replacement in SERVICEPATTERNS:
            m = re.match(pattern, sstring)
            if m:
                return replacement.format(*m.groups())

    # handle snotices
    if re.search(SERVER, nick):
        # remove color and excess whitespace
        sstring = " ".join(weechat.string_remove_color(string, "").split())

        for pattern, replacement in SERVERPATTERNS:
            m = re.match(pattern, sstring)
            if m:
                return replacement.format(*m.groups())

    return string

weechat.hook_modifier("weechat_print", "modifier_cb", "")

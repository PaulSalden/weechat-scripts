# -*- coding: utf-8 -*-
import weechat, re

SCRIPT_NAME    = "operspam"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "redirect undesired oper notices to non-logged and non-relayed buffers"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

# This script redirects specific service notices, identified through patterns. It also redirects
# all server notices. Use WeeChat's notify levels to disable buffer notifications (/help buffer).

# adjust to fit weechat setup
NETWORK = "quakenet"

# adjust to preference
SERVICE = "^N[1-9]?$"
SERVER = "\.quakenet\.org$"
PATTERNS = [
    #"\$c\$",
    "\$t\$ Azubu",
    "\$h\$.*matched",
    "\$h\$.*joined BADCHAN",
    "\$h\$.*was hit by joinflood ID"
]
# empty buffer names hide notices entirely
BUFFERNAMES = {"service": "newspam", "snotice": "snotice"}
NOLOG = True
RELAYHIDE = True

# ------------------------------

buffers = {"service": "", "snotice": ""}

def open_buffer(bufname):
    if not buffers[bufname]:
        buffers[bufname] = weechat.buffer_new(BUFFERNAMES[bufname], "", "", "buffer_close_cb", bufname)
        weechat.buffer_set(buffers[bufname], "title", "{} buffer for {}".format(bufname, NETWORK))

        if NOLOG:
            weechat.buffer_set(buffers[bufname], "localvar_set_no_log", "1")

        if RELAYHIDE:
            weechat.buffer_set(buffers[bufname], "localvar_set_relay", "hard-hide")

def buffer_close_cb(data, buffer):
    buffers[data] = ""
    return weechat.WEECHAT_RC_OK

def do_print(bufname, nick, text):
    if BUFFERNAMES[bufname]:
        open_buffer(bufname)

        # include nick in tags for possible formatting
        tags = "nick_{}".format(nick)

        ncolor = weechat.info_get("irc_nick_color_name", nick)
        printtext = "{}{}{}\t{}".format(weechat.color(ncolor), nick, weechat.color("reset"), text)

        weechat.prnt_date_tags(buffers[bufname], 0, tags, printtext)

def modifier_cb(data, modifier, modifier_data, string):
    if modifier_data != NETWORK:
        return string

    input = weechat.info_get_hashtable("irc_message_parse", { "message": string })

    # handle service notices
    if re.search(SERVICE, input["nick"]):
        if any(re.match(pattern, input["text"]) for pattern in PATTERNS):
            do_print("service", input["nick"], input["text"])
            return ""

    # handle snotices
    if re.search(SERVER, input["nick"]):
        do_print("snotice", input["nick"], input["text"])
        return ""

    return string

weechat.hook_modifier("irc_in_notice", "modifier_cb", "")

# -*- coding: utf-8 -*-
import weechat, re

SCRIPT_NAME    = "newservspam"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "redirect undesired newserv notices to a non-logged and non-relayed buffer"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

# adjust to fit weechat setup
NETWORK = "quakenet"

# adjust to preference
SERVICES = ["N", "N4"]
PATTERNS = ["\$c\$", "\$t\$ Azubu"]
BUFFERNAME = "newspam" # empty to hide spam entirely
NOLOG = True
RELAYHIDE = True

# to disable notification of spam in hotlist and bufferlist, use:
#   /set weechat.notify.python.<buffername> none
# (/save makes configuration changes persist)

spambuffer = ""
def open_spambuffer():
    global spambuffer
    if not spambuffer:
        spambuffer = weechat.buffer_new(BUFFERNAME, "", "", "spambuffer_close_cb", "")
        weechat.buffer_set(spambuffer, "title", "newserv spam buffer")

        if NOLOG:
            weechat.buffer_set(spambuffer, "localvar_set_no_log", "1")

        if RELAYHIDE:
            weechat.buffer_set(spambuffer, "localvar_set_relay", "hard-hide")

def spambuffer_close_cb(data, buffer):
    global spambuffer
    spambuffer = ""
    return weechat.WEECHAT_RC_OK

def modifier_cb(data, modifier, modifier_data, string):
    if modifier_data != NETWORK:
        return string

    input = weechat.info_get_hashtable("irc_message_parse", { "message": string })
    if input["nick"] not in SERVICES:
        return string

    if not any(re.match(pattern, input["text"]) for pattern in PATTERNS):
        return string

    if BUFFERNAME:
        open_spambuffer()

        ncolor = weechat.info_get("irc_nick_color_name", input["nick"])
        printtext = "{}{}{}\t{}".format(weechat.color(ncolor), input["nick"], weechat.color("reset"), input["text"])
        weechat.prnt(spambuffer, printtext)
    
    return ""

weechat.hook_modifier("irc_in_notice", "modifier_cb", "")

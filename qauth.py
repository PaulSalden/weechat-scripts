# -*- coding: utf-8 -*-
import weechat, hmac, hashlib

SCRIPT_NAME    = "qauth"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.5"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "auth with Q, obtain a hidden host and join channels"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

# set to weechat network name
QUAKENET = "quakenet"

# script related options
OPTIONS = {
    "username": "Q account name",
    "password": "Q account password",
    "channels": "channels to join; see \"/help irc.server.{}.autojoin\" for format".format(QUAKENET)
}

# pause between auth attempts in milliseconds
DELAY = 5 * 60 * 1000

for option, desc in OPTIONS.iteritems():
    if not weechat.config_is_set_plugin(option):
        weechat.config_set_plugin(option, "")
        weechat.config_set_desc_plugin(option, desc)

def _get_script_option(option):
    return weechat.config_string(weechat.config_get("plugins.var.python.{}.{}".format(SCRIPT_NAME, option)))

# based on http://script.quakenet.org/wiki/ChallengeAuth
def _irc_lower(string):
    string = string.lower()

    SYMREP = {"[": "{", "]": "}", "\\": "|", "^": "~"}
    for char, rep in SYMREP.iteritems():
        string = string.replace(char, rep)

    return string

# from https://www.quakenet.org/development/challengeauth
def challengeauth(lcusername, truncpassword, challenge, digest=hashlib.sha256):
    return hmac.HMAC(digest("{}:{}".format(lcusername, digest(truncpassword).hexdigest())).hexdigest(),
        challenge, digestmod=digest).hexdigest()

# make sure channels are not joined after /sethost
authwait = False
timer = ""

def connected_cb(data, signal, signal_data):
    global authwait, timer
    if signal_data == QUAKENET:
        username = _get_script_option("username")
        password = _get_script_option("password")

        if username and password:
            nick = weechat.info_get("irc_nick", QUAKENET)
            authwait = True
            timer = weechat.hook_timer(DELAY, 0, 0, "timer_cb", "")
            # /mode does not support -server
            weechat.command("", "/quote -server {} mode {} +x".format(QUAKENET, nick))
            weechat.command("", "/msg -server {} q@cserve.quakenet.org CHALLENGE".format(QUAKENET))
    return weechat.WEECHAT_RC_OK

def notice_cb(data, signal, signal_data):
    if authwait:
        input = weechat.info_get_hashtable("irc_message_parse", {"message": signal_data})

        if input["nick"] == "Q":
            words = input["text"].split()

            if words[0] == "CHALLENGE" and "HMAC-SHA-256" in words[2:]:
                username = _get_script_option("username")
                lcusername = _irc_lower(username)
                truncpassword = _get_script_option("password")[:10]
                response = challengeauth(lcusername, truncpassword, words[1])

                template = "/msg -server {} q@cserve.quakenet.org CHALLENGEAUTH {} {} HMAC-SHA-256"
                weechat.command("", template.format(QUAKENET, username, response))
    return weechat.WEECHAT_RC_OK

def hidden_host_cb(data, signal, signal_data):
    global authwait, timer
    if authwait:
        authwait = False
        weechat.unhook(timer)
        timer = ""
        channels = _get_script_option("channels")

        if channels:
            weechat.command("", "/join -server {} {}".format(QUAKENET, channels))
    return weechat.WEECHAT_RC_OK

# prevent (automatic) joins while the authentication process is ongoing
def join_modifier_cb(data, modifier, modifier_data, string):
    if authwait and modifier_data == QUAKENET:
        return ""
    return string

# retry auth until it succeeds
def timer_cb(data, remaining_calls):
    weechat.command("", "/msg -server {} q@cserve.quakenet.org CHALLENGE".format(QUAKENET))
    return weechat.WEECHAT_RC_OK

weechat.hook_signal("irc_server_connected", "connected_cb", "")
weechat.hook_signal("{},irc_in_notice".format(QUAKENET), "notice_cb", "")
weechat.hook_signal("{},irc_in_396".format(QUAKENET), "hidden_host_cb", "")
weechat.hook_modifier("irc_out_join", "join_modifier_cb", "")
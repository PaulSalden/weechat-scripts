# -*- coding: utf-8 -*-
import weechat

SCRIPT_NAME    = "qauth"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "1.0"
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

for option, desc in OPTIONS.iteritems():
    if not weechat.config_is_set_plugin(option):
        weechat.config_set_plugin(option, "")
        weechat.config_set_desc_plugin(option, desc)

def _get_script_option(option):
    return weechat.config_string(weechat.config_get("plugins.var.python.{}.{}".format(SCRIPT_NAME, option)))

# make sure channels are not joined after /sethost
authwait = False

def connected_cb(data, signal, signal_data):
    global authwait
    if signal_data == QUAKENET:
        username = _get_script_option("username")
        password = _get_script_option("password")

        if username and password:
            nick = weechat.info_get("irc_nick", QUAKENET)
            authwait = True
            # /mode does not support -server
            weechat.command("", "/quote -server {} mode {} +x".format(QUAKENET, nick))
            weechat.command("", "/quote -server {} auth {} {}".format(QUAKENET, username, password))
    return weechat.WEECHAT_RC_OK

def hidden_host_cb(data, signal, signal_data):
    global authwait
    if authwait:
        authwait = False
        channels = _get_script_option("channels")

        if channels:
            weechat.command("", "/join -server {} {}".format(QUAKENET, channels))
    return weechat.WEECHAT_RC_OK

weechat.hook_signal("irc_server_connected", "connected_cb", "")
weechat.hook_signal("{},irc_in_396".format(QUAKENET), "hidden_host_cb", "")

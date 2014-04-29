# -*- coding: utf-8 -*-
import weechat, urllib2, json

SCRIPT_NAME    = "pubstats"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org"
SCRIPT_VERSION = "0.0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "request public stats upon channel join and print a warning if they are available"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

def _api_url(channel):
    return 'https://stats.quakenet.org/api/channel/' + channel

def joined_cb(data, signal, signal_data):
    bufpoint = signal_data
    bufname = weechat.buffer_get_string(bufpoint, "name")
    channel = bufname.split("#")[1]

    try:
        apirequest = urllib2.Request(_api_url(channel))
        apiresult = urllib2.urlopen(apirequest)
        apidata = json.loads(apiresult.read())
    except:
        weechat.prnt(bufpoint, weechat.color("chat_highlight")+"unable to obtain stats data")
    else:
        if "success" not in apidata:
            weechat.prnt(bufpoint, weechat.color("chat_highlight")+"warning: public stats available!")
    
    return weechat.WEECHAT_RC_OK

weechat.hook_signal("irc_channel_opened", "joined_cb", "")

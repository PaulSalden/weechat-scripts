# -*- coding: utf-8 -*-
import weechat, datetime

SCRIPT_NAME    = "nextep"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org"
SCRIPT_VERSION = "0.0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "provide airtime of next GoT episode"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

#datetime(year, month, day, hour, minute)
EPISODES = [
    (datetime.datetime(2014, 4, 21, 3, 0), "Breaker of Chains"),
    (datetime.datetime(2014, 4, 28, 3, 0), "Oathkeeper"),
    (datetime.datetime(2014, 5, 5, 3, 0), "First of His Name"),
    (datetime.datetime(2014, 5, 12, 3, 0), "The Laws of Gods and Men"),
    (datetime.datetime(2014, 5, 19, 3, 0), "Mockingbird"),
    (datetime.datetime(2014, 6, 2, 3, 0), "Episode #4.8"),
    (datetime.datetime(2014, 6, 9, 3, 0), "Episode #4.9"),
    (datetime.datetime(2014, 6, 16, 3, 0), "Episode #4.10"),
]

def _get_buffer(server, channel):
    return weechat.info_get("irc_buffer", ",".join((server, channel)))

def _find_nextep():
    for ep in EPISODES:
        if ep[0] > datetime.datetime.now():
            return ep
    return ()

def _readable_time_remaining(delta):
    rem_days = delta.days
    rem_hours = delta.seconds / 3600
    if rem_days: return "{} days and {} hours".format(rem_days, rem_hours)
    return "{} hours".format(rem_hours)

def nextep_response():
    nextep = _find_nextep()
    if not nextep: return "season is finished"
    delta = nextep[0] - datetime.datetime.now()
    remaining = _readable_time_remaining(delta)
    title = nextep[1]
    return "\"{}\" in {}".format(title, remaining)

def msg_cb(data, signal, signal_data):
    server = signal.split(",")[0]
    input = weechat.info_get_hashtable("irc_message_parse", { "message": signal_data })
    message = input["arguments"].split(":", 1)[-1]

    if message == "!nextepisode":
        buffer = _get_buffer(server, input["channel"])
        if buffer:
            response = nextep_response()
            weechat.command(buffer, response)
    return weechat.WEECHAT_RC_OK

weechat.hook_signal("*,irc_in2_privmsg", "msg_cb", "")

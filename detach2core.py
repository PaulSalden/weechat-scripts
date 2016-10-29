# -*- coding: utf-8 -*-
import weechat, os, re

SCRIPT_NAME    = "detach2core"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "0.0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Make core buffer current when screen/tmux is detached from."

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

# check interval in milliseconds
INTERVAL = 5 * 1000

# based on https://weechat.org/scripts/source/screen_away.py.html/

TIMER = None
SOCK = None

def set_timer():
    '''Update timer hook with new interval'''

    global TIMER
    if TIMER:
        weechat.unhook(TIMER)
    TIMER = weechat.hook_timer(INTERVAL, 0, 0, "timer_cb", '')

def timer_cb(buffer, args):
    '''Check if screen is attached, switch buffer'''

    global SOCK

    attached = os.access(SOCK, os.X_OK) # X bit indicates attached

    if not attached:
    	weechat.command("", "/buffer 1")

    return weechat.WEECHAT_RC_OK

# determine socket and set timer accordingly

if 'STY' in os.environ.keys():
    # We are running under screen
    cmd_output = os.popen('env LC_ALL=C screen -ls').read()
    match = re.search(r'Sockets? in (/.+)\.', cmd_output)
    if match:
        SOCK = os.path.join(match.group(1), os.environ['STY'])

if not SOCK and 'TMUX' in os.environ.keys():
    # We are running under tmux
    socket_data = os.environ['TMUX']
    SOCK = socket_data.rsplit(',',2)[0]

if SOCK:
    set_timer()
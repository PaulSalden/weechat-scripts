# -*- coding: utf-8 -*-
import weechat, pickle
from random import choice

SCRIPT_NAME    = "collections"
SCRIPT_AUTHOR  = "Paul Salden <voronoi@quakenet.org>"
SCRIPT_VERSION = "0.0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "keep a collection of !triggerable items"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
    SCRIPT_LICENSE, SCRIPT_DESC, "", "")

DB = {}
try:
    DB = pickle.load(open("collections.p", "rb"))
except: pass



def saveDB():
    try:
        pickle.dump(DB, open("collections.p", "wb"))
    except: pass

def print_per_10(items):
    for i in range(0, len(items), 10):
        weechat.prnt("", "  " + ", ".join(items[i:i+10]))

def add_collection(*args):
    if len(args) != 1: return "incorrect syntax"
    collection = args[0]
    if collection in DB: return "collection exists"
    DB[collection] = {
        "aliases": {},
        "items": {},
    }
    saveDB()
    return "collection {} created".format(collection)

def rem_collection(*args):
    if len(args) != 1: return "incorrect syntax"
    collection = args[0]
    if collection not in DB: return "collection does not exist"
    del DB[collection]
    saveDB()
    return "collection {} deleted".format(collection)

def list_collections():
    print_per_10(sorted(DB))
    return "done"

def add_value(*args):
    if len(args) != 3: return "incorrect syntax"
    collection, item, value = args
    if collection not in DB: return "collection does not exist"
    if item not in DB[collection]["items"]:
        DB[collection]["items"][item] = [value]
        saveDB()
        return "item {} created".format(item)
    DB[collection]["items"][item].append(value)
    saveDB()
    return "value added to {}".format(item)

def rem_value(*args):
    if len(args) != 3: return "incorrect syntax"
    collection, item, value = args
    if collection not in DB: return "collection does not exist"
    if item not in DB[collection]["items"]: return "item does not exist"
    if value not in DB[collection]["items"][item]: return "value does not exist"
    DB[collection]["items"][item].remove(value)
    if not DB[collection]["items"][item]:
        del DB[collection]["items"][item]
        saveDB()
        return "item {} removed".format(item)
    saveDB()
    return "value removed from {}".format(item)

def list_items(*args):
    if len(args) != 1: return "incorrect syntax"
    collection = args[0]
    if collection not in DB: return "collection does not exist"
    print_per_10(sorted(DB[collection]["items"]))
    return "done"

def list_values(*args):
    if len(args) != 2: return "incorrect syntax"
    collection, item = args
    if collection not in DB: return "collection does not exist"
    if item not in DB[collection]["items"]: return "item does not exist"
    print_per_10(sorted(DB[collection]["items"][item]))
    return "done"

def add_alias(*args):
    if len(args) != 3: return "incorrect syntax"
    collection, item, alias = args
    if collection not in DB: return "collection does not exist"
    if item not in DB[collection]["items"]: return "item does not exist"
    if alias in DB[collection]["aliases"]: return "alias exists"
    DB[collection]["aliases"][alias] = item
    saveDB()
    return "alias added for {}".format(item)

def rem_alias(*args):
    if len(args) != 2: return "incorrect syntax"
    collection, alias = args
    if collection not in DB: return "collection does not exist"
    if alias not in DB[collection]["aliases"]: return "alias does not exist"
    item = DB[collection]["aliases"].pop(alias)
    saveDB()
    return "alias for {} removed".format(item)

def list_aliases(*args):
    if len(args) != 2: return "incorrect syntax"
    collection, item = args
    if collection not in DB: return "collection does not exist"
    aliases = [key for key, value in DB[collection]["aliases"].iteritems()
        if value == item]
    print_per_10(sorted(aliases))
    return "done"
    


def _collection_entry(collection, item):
    if item in DB[collection]["aliases"]: item = DB[collection]["aliases"][item]
    if not item in DB[collection]["items"]: return ""
    return choice(DB[collection]["items"][item])

def _get_buffer(server, channel):
    return weechat.info_get("irc_buffer", ",".join((server, channel)))

def cols_cb(data, buffer, args):
    args = args.split()
    FUNCS = {
        "add": add_collection,
        "rem": rem_collection,
        "list": list_collections,
        "addvalue": add_value,
        "remvalue": rem_value,
        "listitems": list_items,
        "listvalues": list_values,
        "addalias": add_alias,
        "remalias": rem_alias,
        "listaliases": list_aliases,
    }
    if args[0] in FUNCS:
        out = FUNCS[args[0]](*args[1:])
        weechat.prnt("", out)
    else:
        weechat.prnt("", "incorrect syntax")
    return weechat.WEECHAT_RC_OK

def msg_cb(data, signal, signal_data):
    server = signal.split(",")[0]
    input = weechat.info_get_hashtable("irc_message_parse", { "message": signal_data })
    message = input["arguments"].split(":", 1)[-1]
    words = message.split()

    if len(words) == 2 and words[0][0] == "!":
        collection = words[0][1:]
        item = words[1].lower()
        if collection in DB:
            response = _collection_entry(collection, item)
            buffer = _get_buffer(server, input["channel"])
            if response and buffer: weechat.command(buffer, response)
    return weechat.WEECHAT_RC_OK



hook = weechat.hook_command("cols", "handle collections",
    "[add|rem|list [collection]] | [addvalue|remvalue|listvalues [collection] [item] [value]]"
    "| [addalias|remalias|listalias [collection] [item] [alias]]",
    "t.b.d. description of arguments...",
    "add"
    " || rem"
    " || list"
    " || addvalue"
    " || remvalue"
    " || listitems"
    " || listvalues"
    " || addalias"
    " || remalias"
    " || listaliases",
    "cols_cb", "")
weechat.hook_signal("*,irc_in2_privmsg", "msg_cb", "")

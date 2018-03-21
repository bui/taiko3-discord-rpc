#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import time

from binascii import hexlify

if sys.version_info < (3, 0):
    sys.exit('This program only runs on Python 3.')

try:
    import tcpgecko
except ModuleNotFoundError:
    sys.exit('tcpgecko.py not found! Download it (and common.py) from https://github.com/wiiudev/pyGecko\n'
             'Make sure to also convert tcpgecko.py to Python 3 code - use the 2to3 tool for this')

try:
    import pypresence
except ModuleNotFoundError:
    sys.exit('pypresence.py not found! Download it from https://github.com/qwertyquerty/pypresence')

MODES = {
    6: ('In a menu', 'Title Screen'),
    7: ('In a menu', 'Player Entry'),
    8: ('In a menu', 'Mode Select'),

    9: ('Taiko Mode', 'Song Select'),
    10: ('Baton Touch', 'Song Select'),

    11: ('Playing song',),
    12: ('Results',),

    13: ('Kisekae Studio',),
    14: ('Intro-don',),
    15: ('Mecha-don Gacha',),

    16: ('In a menu', 'Stats'),
    17: ('Looking at stats', 'Stamp Book'),
    18: ('Looking at stats', 'Player Stats'),
    19: ('Looking at stats', 'Seals'),

    20: ('In a menu', 'Additional Content'),
    21: ('In a menu', 'Settings'),
    22: ('Tutorial',),

    24: ('In a menu', 'Tomodachi Daisakusen'),
    25: ('Tomodachi Daisakusen', 'On the streets'),
    26: ('Tomodachi Daisakusen', 'Results'),
    28: ('Tomodachi Daisakusen', 'Wada House'),
    29: ('Tomodachi Daisakusen', 'Friend Book'),
    30: ('Tomodachi Daisakusen', 'Settings'),
    31: ('Tomodachi Daisakusen', 'Difficulty Select'),

    32: ('Tomodachi Daisakusen', 'In a cutscene'),
    33: ('Tomodachi Daisakusen', 'In a cutscene'),
    34: ('In a cutscene',)
}

LEVELS = {
    0: 'Easy',
    1: 'Normal',
    2: 'Hard',
    3: 'Extreme'
}

SONG_MODES = {
    0: 'Taiko Mode',
    1: 'Tomodachi Daisakusen',
    2: 'Baton Touch'
}

TAIKO_TITLE = 0x50000101D3000
DEFAULT_CLIENT_ID = 422847967347867654

parser = argparse.ArgumentParser()
parser.add_argument('server', help='console IP address')
parser.add_argument('-c', '--client-id', help='Discord client ID')
parser.add_argument('-l', '--launch-auto', help='launch title automatically if not running', action='store_true')
args = parser.parse_args()


def get_current_title(gecko):
    ver = gecko.getversion()
    if ver == 550:
        loc = 0x10013C10
    elif ver < 550 and ver >= 532:
        loc = 0x100136D0
    elif ver < 532 and ver >= 500:
        loc = 0x10013010
    elif ver == 410:
        loc = 0x1000ECB0
    else:
        sys.exit('Your Wii U firmware version is not supported. Please update.')

    return int(hexlify(gecko.readmem(loc, 8)), 16)


def is_title_installed(gecko, title):
    return gecko.get_symbol('sysapp.rpl', 'SYSCheckTitleExists', True)(title >> 32, title & 0xFFFFFFFF)


def launch_title(gecko, title):
    gecko.get_symbol('sysapp.rpl', 'SYSLaunchTitle', True)(title >> 32, title & 0xFFFFFFFF)

    # tcpgecko restarts when title changes, so we need to reconnect
    time.sleep(30)  # safe enough?

    print('Title changed; reconnecting...')
    gecko = tcpgecko.TCPGecko(args.server)
    return gecko


if __name__ == '__main__':
    try:
        songlist = json.loads(open('data/song_data.json', 'r').read())
    except FileNotFoundError:
        sys.exit('data/song_data.json not found, use extract_songs.py to build it')
    except json.decoder.JSONDecodeError:
        sys.exit('data/song_data.json does not contain valid JSON')

    try:
        gecko = tcpgecko.TCPGecko(args.server)
    except TimeoutError:
        sys.exit('Unable to connect to tcpGecko - are you sure it\'s running on your console?')

    if get_current_title(gecko) != TAIKO_TITLE:
        if args.launch_auto:
            if is_title_installed(gecko, TAIKO_TITLE):
                gecko = launch_title(gecko, TAIKO_TITLE)
            else:
                sys.exit('Taiko no Tatsujin: ATD is not installed on your Wii U.')
        else:
            sys.exit('Taiko no Tatsujin: ATD is not running on your Wii U. Launch it first, or use --launch-auto')

    print('Connecting to Discord RPC...')
    rpc = pypresence.client(args.client_id or str(DEFAULT_CLIENT_ID))
    rpc.start()

    last_event = None
    while True:
        event = int(hexlify(gecko.readmem(0x1056A684, 4)), 16)

        if event != last_event:
            last_event = event
            mode = MODES[event] if event in MODES else None

            song_mode = None
            mode_id = int(hexlify(gecko.readmem(0x10566174, 4)), 16)
            if mode_id in SONG_MODES:
                song_mode = SONG_MODES[mode_id]

            if event == 11:
                course = int(hexlify(gecko.readmem(0x1058AB9C, 4)), 16)
                difficulty = int(hexlify(gecko.readmem(0x1058A960, 4)), 16)
                level = LEVELS[difficulty]

                song_title = '???'
                if str(course) in songlist:
                    song = songlist[str(course)]
                    song_title = song['title']
                    song_stars = song['stars'][str(difficulty)]
                    level = '%s (%s\u2605)' % (level, song_stars)

                rpc.set_activity(state=song_mode, details=song['title'], large_image='taiko',
                                 small_image='level_%s' % difficulty, small_text=level)
            elif event == 12:
                rpc.set_activity(state=song_mode, details=mode[0], large_image='taiko')
            elif mode:
                rpc.set_activity(state=mode[0], details=mode[1] if len(mode) > 1 else None, large_image='taiko')

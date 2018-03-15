#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import tcpgecko
import pypresence
import sys

from binascii import hexlify

MODES = {
    6: ('In a menu', 'Title Screen'),
    7: ('In a menu', 'Player Entry'),
    8: ('In a menu', 'Main Menu'),

    9: ('Taiko Mode', 'Selecting a song'),
    10: ('Baton Touch', 'Selecting a song'),

    11: ('Taiko Mode',),
    12: ('Taiko Mode', 'Viewing results'),

    13: ('Kisekae Studio',),
    14: ('Intro-don',),
    15: ('Mecha-don Gacha',),

    16: ('In a menu', 'Stats'),
    17: ('Looking at stats', 'Stamp Book'),
    18: ('Looking at stats', 'Player Stats'),
    19: ('Looking at stats', 'Seals'),

    20: ('In a menu', 'Additional Content'),
    21: ('In a menu', 'Settings'),
    22: ('Playing tutorial',),

    24: ('In a menu', 'Tomodachi Daisakusen'),
    25: ('Tomodachi Daisakusen', 'On the streets'),
    26: ('Tomodachi Daisakusen', 'Viewing results'),
    28: ('Tomodachi Daisakusen', 'Wada House'),
    29: ('Tomodachi Daisakusen', 'Friend Book'),
    30: ('Tomodachi Daisakusen', 'Settings'),
    31: ('Tomodachi Daisakusen', 'Selecting difficulty'),

    32: ('Tomodachi Daisakusen', 'In a cutscene'),
    33: ('Tomodachi Daisakusen', 'In a cutscene'),
    34: ('In a cutscene',)
}

LEVELS = {
    0: 'Easy',
    1: 'Medium',
    2: 'Hard',
    3: 'Extreme'
}

parser = argparse.ArgumentParser()
parser.add_argument('server', help='console IP address')
parser.add_argument('client_id', help='Discord client ID')
args = parser.parse_args()


if __name__ == '__main__':
    print('Connecting to tcpGecko...')
    gecko = tcpgecko.TCPGecko(args.server)

    songlist = json.loads(open('song_data.json', 'r').read())

    print('Connecting to Discord RPC...')
    rpc = pypresence.client(args.client_id)
    rpc.start()

    last_event = None
    last_select = None
    while True:
        event = int(hexlify(gecko.readmem(0x1056A684, 4)), 16)

        if event != last_event:
            last_event = event

            if event == 11:
                course = int(hexlify(gecko.readmem(0x1058AB9C, 4)), 16)
                difficulty = int(hexlify(gecko.readmem(0x1058A960, 4)), 16)
                level = LEVELS[difficulty]

                song_title = '???'
                if str(course) in songlist:
                    song_title = songlist[str(course)]

                rpc.set_activity(state=MODES[event][0],
                                 details=song_title, large_image='taiko',
                                 small_image='df_%s' % level.lower(),
                                 small_text=level)

            elif event in MODES:
                mode = MODES[event]
                rpc.set_activity(state=mode[0], details=mode[1] if len(mode) > 1 else None,
                                 large_image='taiko')

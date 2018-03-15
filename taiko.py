#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import tcpgecko
import pypresence
import sys

from binascii import hexlify

MODES = {
    0: 'Starting up',
    2: 'Saving game',
    3: 'Checking DLC',
    5: '???',
    6: 'On title screen',
    7: 'Selecting players',
    8: 'In main menu',
    9: 'Selecting a song',
    10: 'Selecting a baton song',
    11: 'Playing a song',
    12: 'Viewing results',
    13: 'Making a Don',
    14: 'Playing Intoro-don',
    15: 'Mecha-don Gacha',
    16: 'In stats menu',
    17: 'Viewing stamps',
    18: 'Viewing player stats',
    19: 'Hanko',
    20: 'In DLC menu',
    21: 'In settings menu',
    22: 'Playing tutorial',
    24: 'Tomodachi main menu',
    25: 'Tomodachi select',
    26: 'Tomodachi results',
    28: 'Tomodachi home',
    29: 'Tomodachi collection',
    30: 'Tomodachi settings',
    31: 'Tomodachi difficulty select',
    32: 'Tomodachi cutscene',
    34: '15th cutscene'
}

LEVELS = {
    0: 'Easy',
    16777216: 'Medium',
    33554432: 'Hard',
    50331648: 'Extreme'
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
    while True:
        event = int(hexlify(gecko.readmem(0x1056A684, 4)), 16)

        if event != last_event:
            last_event = event

            if event == 11:
                course = int(hexlify(gecko.readmem(0x105F41E8, 4)), 16)
                difficulty = int(hexlify(gecko.readmem(0x105F41EC, 4)), 16)
                level = LEVELS[difficulty]

                song_title = '???'
                if str(course) in songlist:
                    song_title = songlist[str(course)]

                rpc.set_activity(state=MODES[event],
                                 details='%s on %s' % (song_title, level),
                                 large_image='taiko', small_image='df_%s' % level.lower(),
                                 small_text=level)

            elif event not in [0, 2, 3, 5]:
                rpc.set_activity(state=MODES[event], large_image='taiko')

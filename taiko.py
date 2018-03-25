#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import os
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


parser = argparse.ArgumentParser()
parser.add_argument('server', help='console IP address')
parser.add_argument('-c', '--client-id', help='Discord client ID')
parser.add_argument('-l', '--launch-auto', help='launch title automatically if not running', nargs='?', default=argparse.SUPPRESS)
parser.add_argument('-j', '--jump', help='allow title jumping with --launch-auto', action='store_true')
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
    titles = os.listdir('data')

    try:
        gecko = tcpgecko.TCPGecko(args.server)
    except TimeoutError:
        sys.exit('Unable to connect to tcpGecko - are you sure it\'s running on your console?')

    current = get_current_title(gecko)
    cur = None
    all_ids = []
    for title in titles:
        vals = json.loads(open('data/%s/values.json' % title, encoding='utf8').read())
        all_ids.append((title, vals['title_id'], vals['title']))

        if vals['title_id'] == current:
            songlist = json.loads(open('data/%s/song_data.json' % title).read())
            cur = vals

    if args.jump or not cur:
        if hasattr(args, 'launch_auto') is not False:
            launchable = []
            for tid in all_ids:
                if is_title_installed(gecko, tid[1]):
                    if args.launch_auto is None or args.launch_auto == tid[0]:
                        launchable.append(tid)

            if len(launchable) > 1:
                print('There is more than one Taiko no Tatsujin title installed on your Wii U. '
                      'Supply the desired title to launch it, eg. --launch-auto wiiu3\n\n'
                      'Installed titles:')

                for title in launchable:
                    print('%s = %s' % (title[0], title[2]))

                sys.exit()
            elif not launchable:
                sys.exit('There are no Taiko no Tatsujin titles installed on your Wii U.')
            elif launchable[0][1] != current:
                gecko = launch_title(gecko, launchable[0][1])
                cur = json.loads(open('data/%s/values.json' % launchable[0][0], encoding='utf8').read())
                songlist = json.loads(open('data/%s/song_data.json' % launchable[0][0]).read())

        else:
            sys.exit('There is no Taiko no Tatsujin title running on your Wii U. Launch one first, or use --launch-auto')

    print('Connecting to Discord RPC...')
    rpc = pypresence.client(args.client_id or str(cur['default_client_id']))
    rpc.start()

    last_event = None
    while True:
        event = str(int(hexlify(gecko.readmem(cur['pointers']['mode'], 4)), 16))

        if event != last_event:
            last_event = event
            mode = cur['modes'][event] if event in cur['modes'] else None

            song_mode = None
            mode_id = str(int(hexlify(gecko.readmem(cur['pointers']['song_mode'], 4)), 16))
            if mode_id in cur['song_modes']:
                song_mode = cur['song_modes'][mode_id]

            if event == '11':
                course = int(hexlify(gecko.readmem(cur['pointers']['song'], 4)), 16)
                difficulty = str(int(hexlify(gecko.readmem(cur['pointers']['difficulty'], 4)), 16))
                level = cur['levels'][difficulty]

                song_title = '???'
                if str(course) in songlist:
                    song = songlist[str(course)]
                    song_title = song['title']
                    song_stars = song['stars'][str(difficulty)]
                    level = '%s (%s\u2605)' % (level, song_stars)

                rpc.set_activity(state=song_mode, details=song_title, large_image='taiko',
                                 small_image='level_%s' % difficulty, small_text=level)
            elif event == '12':
                rpc.set_activity(state=song_mode, details=mode[0], large_image='taiko')
            elif mode:
                rpc.set_activity(state=mode[0], details=mode[1] if len(mode) > 1 else None, large_image='taiko')

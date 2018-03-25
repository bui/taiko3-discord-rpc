#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path
import xml.etree.cElementTree
import zlib

from io import BytesIO
from struct import unpack

DIRS = \
    {'wiiu': {
        'base': r'D:\WUP\DATA\EMULATORS\Cemu\GAMES\Taiko no Tatsujin Wii U version! [AT5JAF]',
        'update': r'D:\WUP\DATA\EMULATORS\Cemu\BIN\mlc01\usr\title\00050000\10132200'
    }, 'wiiu2': {
        'base': r'D:\WUP\DATA\EMULATORS\Cemu\GAMES\Taiko no Tatsujin Tokumori! [BT9JAF]',
        'update': r'D:\WUP\DATA\EMULATORS\Cemu\BIN\mlc01\usr\title\00050000\10192000'
    }, 'wiiu3': {
        'base': r'D:\WUP\DATA\EMULATORS\Cemu\GAMES\Taiko no Tatsujin Atsumete TomodachiDaisakusen! [BT3JAF]',
        'update': r'D:\WUP\DATA\EMULATORS\Cemu\BIN\mlc01\usr\title\00050000\101d3000'
    }}


def process_drp(path, search, taiko):
    proc_songs = {}

    drp = open(path, 'rb')
    drp.seek(0x14)

    unknown, fcount = unpack('>HH', drp.read(4))
    drp.seek(0x60)
    
    for i in range(0, fcount):
        fname = drp.read(0x40).split(b'\x00')[0]
        
        drp.seek(0x10, 1)
        fsize, fsize2, fsize3, fsize4, uncompressedsize = unpack('>5I', drp.read(4*5))
        data = drp.read(fsize2-4)
        if fsize > 80:
            data = zlib.decompress(data)

        if fname != search:
            continue

        drp2 = BytesIO(data)
        drp3 = xml.etree.cElementTree.parse(drp2).getroot()

        for song in drp3.findall('DATA_SET'):
            song_id = song.find('uniqueId').text
            song_title = song.find('title').text

            stars_easy = int(song.find('starEasy').text)
            stars_normal = int(song.find('starNormal').text)
            stars_hard = int(song.find('starHard').text)
            stars_extreme = int(song.find('starMania').text)

            level_keys = list(json.loads(open('data/%s/values.json' % taiko, encoding='utf8').read())['levels'].keys())
            if song_id not in songs.keys():
                proc_songs[song_id] = {'title': song_title,
                                       'stars': {level_keys[0]: stars_easy, level_keys[1]: stars_normal,
                                                 level_keys[2]: stars_hard, level_keys[3]: stars_extreme}}

    drp.close()
    return proc_songs


if __name__ == '__main__':
    for k, v in DIRS.items():
        songs = {}

        base_songs = process_drp(os.path.join(v['base'], r'content\Common\database\db_pack.drp'), b'musicinfo_db', k)
        songs = base_songs

        for path, dirs, files in os.walk(os.path.join(v['update'], r'aoc\content')):
            if 'musicInfo.drp' in files:
                dlc = process_drp(os.path.join(path, 'musicInfo.drp'), b'musicinfo_db', k)
                tmps = songs.copy()
                tmps.update(dlc)
                songs = tmps

        with open('data/%s/song_data.json' % k, 'w') as fp:
            fp.write(json.dumps(songs))
            fp.close()

        print('%s: Wrote %d songs!' % (k, len(songs)))

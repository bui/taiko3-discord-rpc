#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path
import xml.etree.cElementTree
import zlib

from io import BytesIO
from struct import unpack

DIRS = {
    'base': r'D:\WUP\DATA\EMULATORS\Cemu\GAMES\Taiko no Tatsujin Atsumete TomodachiDaisakusen! [BT3JAF]',
    'update': r'D:\WUP\DATA\EMULATORS\Cemu\BIN\mlc01\usr\title\00050000\101d3000'
}


def process_drp(path, search):
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

            if song_id not in songs.keys():
                proc_songs[song_id] = song_title

    drp.close()
    return proc_songs


if __name__ == '__main__':
    songs = {}

    base_songs = process_drp(os.path.join(DIRS['base'], r'content\Common\database\db_pack.drp'), b'musicinfo_db')
    songs = base_songs

    for path, dirs, files in os.walk(os.path.join(DIRS['update'], r'aoc\content')):
        if 'musicInfo.drp' in files:
            dlc = process_drp(os.path.join(path, 'musicInfo.drp'), b'musicinfo_db')
            tmps = songs.copy()
            tmps.update(dlc)
            songs = tmps

    with open('data/song_data.json', 'w') as fp:
        fp.write(json.dumps(songs))
        fp.close()

    print('Wrote %d songs!' % len(songs))

#!/usr/bin/python
# -*- coding: UTF-8 -*-

# ---
# iPIN - iPhone PNG Images Normalizer v1.0
# Copyright (C) 2007
#
# Author:
#  Axel E. Brzostowski
#  http://www.axelbrz.com.ar/
#  axelbrz@gmail.com
#
# References:
#  http://iphone.fiveforty.net/wiki/index.php/PNG_Images
#  http://www.libpng.org/pub/png/spec/1.2/PNG-Contents.html
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# ---

import os
import stat
from struct import *
from zlib import *


def getNormalizedPNG(filename):
    pngheader = b"\x89PNG\r\n\x1a\n"

    file = open(filename, "rb")
    oldPNG = file.read()
    file.close()

    if oldPNG[:8] != pngheader:
        return None

    newPNG = oldPNG[:8]

    chunkPos = len(newPNG)

    idatAcc = b""
    breakLoop = False

    # For each chunk in the PNG file
    while chunkPos < len(oldPNG):
        skip = False

        # Reading chunk
        chunkLength = oldPNG[chunkPos:chunkPos + 4]
        chunkLength = unpack(">L", chunkLength)[0]
        chunkType = oldPNG[chunkPos + 4: chunkPos + 8]
        chunkData = oldPNG[chunkPos + 8:chunkPos + 8 + chunkLength]
        chunkCRC = oldPNG[chunkPos + chunkLength + 8:chunkPos + chunkLength + 12]
        chunkCRC = unpack(">L", chunkCRC)[0]
        chunkPos += chunkLength + 12

        # Parsing the header chunk
        if chunkType == b"IHDR":
            width = unpack(">L", chunkData[0:4])[0]
            height = unpack(">L", chunkData[4:8])[0]

        # Parsing the image chunk
        if chunkType == b"IDAT":
            # Store the chunk data for later decompression
            idatAcc += chunkData
            skip = True

        # Removing CgBI chunk
        if chunkType == b"CgBI":
            skip = True

        # Add all accumulated IDATA chunks
        if chunkType == b"IEND":
            try:
                # Uncompressing the image chunk
                bufSize = width * height * 4 + height
                chunkData = decompress(idatAcc, -15, bufSize)

            except Exception as e:
                return None

            chunkType = b"IDAT"

            # Swapping red & blue bytes for each pixel
            newdata = bytearray(b"")
            for y in range(height):
                i = len(newdata)
                # newdata += chunkData[i]
                newdata.append(chunkData[i])
                for x in range(width):
                    i = len(newdata)
                    newdata.append(chunkData[i + 2])
                    newdata.append(chunkData[i + 1])
                    newdata.append(chunkData[i + 0])
                    newdata.append(chunkData[i + 3])
                    # newdata += chunkData[i + 2]
                    # newdata += chunkData[i + 1]
                    # newdata += chunkData[i + 0]
                    # newdata += chunkData[i + 3]

            # Compressing the image chunk
            chunkData = newdata
            chunkData = compress(chunkData)
            chunkLength = len(chunkData)
            chunkCRC = crc32(chunkType)
            chunkCRC = crc32(chunkData, chunkCRC)
            chunkCRC = (chunkCRC + 0x100000000) % 0x100000000
            breakLoop = True

        if not skip:
            newPNG += pack(">L", chunkLength)
            newPNG += chunkType
            if chunkLength > 0:
                newPNG += chunkData
            newPNG += pack(">L", chunkCRC)
        if breakLoop:
            break

    return newPNG


def updatePNG(filename):
    data = getNormalizedPNG(filename)
    if data != None:
        file = open(filename, "wb")
        file.write(data)
        file.close()
        return True
    return data


def getFiles(base):
    global _dirs
    global _pngs
    if base == ".":
        _dirs = []
        _pngs = []

    if base in _dirs:
        return

    files = os.listdir(base)
    for file in files:
        filepath = os.path.join(base, file)
        try:
            st = os.lstat(filepath)
        except os.error:
            continue

        if stat.S_ISDIR(st.st_mode):
            if not filepath in _dirs:
                getFiles(filepath)
                _dirs.append(filepath)

        elif file[-4:].lower() == ".png":
            if not filepath in _pngs:
                _pngs.append(filepath)

    if base == ".":
        return _dirs, _pngs


# print(updatePNG('/Users/denghaizhu/PycharmProjects/appDownloads/downloads/com.medical.gooddoctors.png'))
# print (" iPhone PNG Images Normalizer v1.0")
# dirs, pngs = getFiles(".")
#
# if len(pngs) == 0:
#     print ("[!] Alert: There are no PNG files found. Move this python file to the folder that contains the PNG files to normalize.")
#     exit()
#
# print (" -  %d PNG files were found at this folder (and subfolders)." % len(pngs))
# while True:
#     normalize = raw_input("[?] Do you want to normalize all images (Y/N)? ").lower()
#     if len(normalize) > 0 and (normalize[0] == "y" or normalize[0] == "n"):
#         break
#
# normalized = 0
# if normalize[0] == "y":
#     for ipng in range(len(pngs)):
#         perc = (float(ipng) / len(pngs)) * 100.0
#         if updatePNG(pngs[ipng]):
#             normalized += 1

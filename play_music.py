#!/usr/bin/env python
"""
Copyright (c) 2018 [Raymond Rusk <rusk.raymond@gmail.com>]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import random
import time

import vlc
from pyfiglet import Figlet

from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC

if os.name == "nt":
    import keyboard
else:
    import sys
    import select
    import termios

    class KeyPoller():
        def __enter__(self):
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            return self

        def __exit__(self, type, value, traceback):
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

        def poll(self):
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if not dr == []:
                return sys.stdin.read(1)
            return None

"""
The ballroom dance music is assumed to be organized so that the music
for each dance is in a separate directory:

$HOME/Music/
|--- ChaCha
|--- Foxtrot
|--- Jive
|--- LineDance
|--- PasoDoble
|--- QuickStep
|--- Rumba
|--- Samba
|--- Tango
|--- VienneseWaltz
|--- Waltz
|--- WCS

The line dance selection method used in play_linedance() depends on the title of each line
dance starting with a different character than the first character of all the other line dances.
If that isn't true the selection method used in play_linedance will need to be modified.
"""

shortest_song = 105.0  # only use music greater than of equals to 1m45s
longest_song = 210.0  # only use music less than or equal to 3m30s


def getMusicDir():
    home = os.path.expanduser("~")
    #return os.path.join(home, u"Music")  # Make sure filenames are utf-8 encoded
    return os.path.join(home, u"Music", u"Creena")
    # return os.path.join(home, u"Downloads", u"Music", u"WF")


def getDances():
    dances = ["Waltz", "Tango", "VienneseWaltz", "Foxtrot", "QuickStep", "WCS",
              "ChaCha", "Samba", "Rumba", "PasoDoble", "Jive", "LineDance"]
    return dances


def availableMusicByDance():
    musicDir = getMusicDir()
    dances = getDances()
    musicList = []
    for idx in range(len(dances)):
        dance = dances[idx]
        musicPath = os.path.join(musicDir, dance)
        playlist = []
        if not os.path.isdir(musicPath):
            print("WARNING: The directory " + musicPath + " does not exist.")
        else:
            for (dirpath, dirnames, filenames) in os.walk(musicPath):
                for name in filenames:
                    fullpathname = os.path.join(dirpath, name)
                    filename, file_extension = os.path.splitext(fullpathname)
                    lengthOK = True
                    try:
                        if file_extension == ".mp3":
                            audio = MP3(fullpathname)
                        elif file_extension == ".m4a":
                            audio = MP4(fullpathname)
                        elif file_extension == ".flac":
                            audio = FLAC(fullpathname)
                        else:
                            print "Unrecognized file extension for " + fullpathname
                        if audio.info.length < shortest_song or audio.info.length > longest_song:
                            lengthOK = False
                        # if not lengthOK:
                        #     print audio.filename + " is of length " + str(audio.info.length)
                    except:
                        print "Exception for " + fullpathname
                        pass  # can't determine length
                    if lengthOK or dance == "LineDance":  # some line dances are long
                        playlist.append(os.path.join(dirpath, name))
        # print dance, "has", len(playlist), "selections"
        musicList.append(playlist)
    return musicList


def randomList(a):
    b = []
    for i in range(len(a)):
        element = random.choice(a)
        a.remove(element)
        b.append(element)
    return b


def randomizeMusicByDance(musicList):
    rMusicList = []
    for dance in musicList:
        rMusicList.append(randomList(dance))
    return rMusicList


def validMusicLists(musicL):
    result = True
    for idx in range(len(getDances())):
        for musicfile in musicL[idx]:
            if os.path.isfile(musicfile) and os.access(musicfile, os.R_OK):
                continue
            else:
                print("File {} doesn't exist or isn't readable".format(musicfile))
                result = False
    return result


def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_exception():
    import sys
    print sys.exc_info()[0]
    import traceback
    print traceback.format_exc()
    print "Press Enter to continue ..."
    raw_input()


def is_intString(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def mediaInfo(player):
    media = player.get_media()
    if media is not None:
        media.parse()
        title = media.get_meta(vlc.Meta.Title) or "Unknown song; title"
        artist = media.get_meta(vlc.Meta.Artist) or "Unknown artist"
        album = media.get_meta(vlc.Meta.Album) or "Unknown album"
        return "{:<60}  {:<20}  {:<20}".format(title.encode('ascii', 'ignore'),
                                               artist.encode('ascii', 'ignore'),
                                               album.encode('ascii', 'ignore'))
    else:
        return ""


def getIndexDance(theDance):
    dances = getDances()
    idx = -1
    i = -1
    danceFound = False
    for dance in dances:
        i = i + 1
        if not dance.startswith(theDance):
            continue
        else:
            danceFound = True
            break
    if danceFound:
        idx = i
    return idx

def playing_song(player, song):
    if os.name == 'nt':
        def on_press_reaction(event):
            if event.name == 'space':
                player.pause()
            elif event.name == 'n':
                player.stop()

        keyboard.on_press(on_press_reaction)
        while True:
            if player.is_playing() or player.get_state() == vlc.State.Paused:
                time.sleep(0.1)  # sleep awhile to reduce CPU usage
                continue
            else:
                break
    else:
        with KeyPoller() as keyPoller:
            while True:
                c = keyPoller.poll()
                while keyPoller.poll() is not None:
                    continue  # discard rest of characters after first
                if not c is None:
                    if c == " ":
                        player.pause()
                    elif c == "n":
                        player.stop()
                    elif c == "b":
                        player.stop()
                        player = vlc.MediaPlayer(song)
                        playing = player.play()
                        if playing == -1:
                            print "Failed to replay selection."
                        player.audio_set_volume(100)
                        time.sleep(1)
                        playing_song(player, song)
                    else:
                        pass
                if player.is_playing() or player.get_state() == vlc.State.Paused:
                    time.sleep(1)  # sleep awhile to reduce CPU usage
                    continue
                else:
                    break


def play_music(theNumSel, offset, theFirstDance, danceMusic):
    idx = getIndexDance(theFirstDance)
    if idx < 0:
        print(" Dance not found!!!")
        raw_input("Hit carriage return to exit and rerun program.")
        exit()
    myFig = Figlet(font='standard')
    dances = getDances()
    for i in range(idx, len(dances)):
        dance = dances[i]
        if dance == "LineDance":
            continue  # line dances are handled in play_linedance()
        if dance == "PasoDoble" and theNumSel == 1:
            continue  # skip Paso when playing only one selection per dance
        print myFig.renderText(dance)

        if theNumSel + offset > len(danceMusic[i]):
            print("There are fewer than " + str(theNumSel + offset) + " selections in the "
                  + os.path.join(getMusicDir(), dance) + " folder.")
            continueYN = raw_input("Continue? <Y/N> ").strip()
            if continueYN == 'N' or continueYN == 'n':
                exit()
        playlist = danceMusic[i][offset:]  # music for dance using offset to skip selections previously played

        if dance == "Waltz":
            if offset == 0:  # at beginning of practice session
                print("[Waltz will have an extra selection for volume adjustment]")
                numPlayed = -1
            else:  # on second or later sessions
                # volume adjustment increased number previously selected for Waltz by 1
                playlist = playlist[1:]
                numPlayed = 0
        elif dance == "PasoDoble":
            nextsong = os.path.join(getMusicDir(), dance, "Get Ready for Paso.mp3")
            if not os.path.isfile(nextsong) or not os.access(nextsong, os.R_OK):
                print("File {} doesn't exist or isn't readable".format(nextsong))
            else:
                player = vlc.MediaPlayer(nextsong)
                player.audio_set_volume(100)
                print mediaInfo(player)
                player.play()
                time.sleep(17)
                for level in range(100, 10, -10):
                    player.audio_set_volume(level)
                    time.sleep(1)
                player.stop()
            try:
                while True:
                    skipYN = raw_input("Skip Paso Doble <Y/N>: ").strip()
                    if skipYN.upper() not in ('Y', 'N'):
                        print("Unrecognized input.  Enter either 'Y' or 'N'.")
                    else:
                        break
                if skipYN.upper() == 'Y':
                    numPlayed = theNumSel
                else:
                    numPlayed = theNumSel - 1  # play only one Paso Doble
            except Exception:
                print("Exception reading input.")
                display_exception()
                continue
        else:
            numPlayed = 0

        for song in playlist:
            numPlayed = numPlayed + 1
            if numPlayed > theNumSel:
                break
            try:
                player = vlc.MediaPlayer(song)
                player.audio_set_volume(100)
                infoStr = mediaInfo(player)
                print(infoStr)
                playing = player.play()
                if playing == -1:
                    print "Failed to play selection."
                    numPlayed = numPlayed - 1
            except Exception:
                print "*** Exception occurred ***"
                display_exception()
                numPlayed = numPlayed - 1
                continue
            time.sleep(3)
            playing_song(player, song)

def play_linedance(danceMusic):
    theDance = "LineDance"
    idx = getIndexDance(theDance)
    if idx < 0:
        print(theDance + " not found!!!")
        raw_input("Hit carriage return to continue without " + theDance)
        return
    myFig = Figlet(font='standard')
    print myFig.renderText(theDance)
    playlist = danceMusic[idx]
    playlist.sort()
    infoStr = []
    # The line dance selection method depends on the title of each line dance starting with
    # a different character than the first character of all the other line dances.
    # If that isn't true the selection method will need to be modified.
    print "Available Line Dances:"
    selection = []
    for i in range(len(playlist)):
        song = playlist[i]
        player = vlc.MediaPlayer(song)
        infoStr.append(mediaInfo(player))
        player.stop()
        selection.append(infoStr[i][0])
        print selection[i] + ": " + infoStr[i]
    selectionStr = "Which Line Dance <"
    for i in range(len(selection)):
        selectionStr = selectionStr + selection[i] + "/"
    selectionStr = selectionStr[:-1] + "> or enter 'n' for [n]one: "
    while True:
        lineDance = raw_input(selectionStr).strip()
        lineDance = lineDance.upper()
        if lineDance == 'N':
            return
        elif lineDance not in selection:
            print("Unrecognized line dance selection.  Please try again.")
        else:
            break

    def indexSelected():
        for i in range(len(selection)):
            if selection[i] == lineDance:
                return i
        return -1

    indexS = indexSelected()
    song = playlist[indexS]
    print
    print infoStr[indexS]
    try:
        player = vlc.MediaPlayer(song)
        player.audio_set_volume(100)
        playing = player.play()
        if playing == -1:
            print "Failed to play selection."
    except Exception:
        print "*** Exception occurred ***"
        display_exception()
        return
    time.sleep(1)
    playing_song(player, song)

if __name__ == '__main__':
    try:
        fig = Figlet(font='standard')
        print fig.renderText("MusicPlayer")

        print "Initializing.  This may take a few seconds..."

        theMusic = availableMusicByDance()
        musicLists = randomizeMusicByDance(theMusic)
        if not validMusicLists(musicLists):
            print("Potential issues with playlist.  Continuing but there may be problems...")

        defaultsYN = raw_input("Play two selections per dance starting with Waltz <Y/N>: ").strip()
        if defaultsYN == 'N' or defaultsYN == 'n':
            while True:
                numSel = raw_input("Enter number of selections to play per dance: ").strip()
                if numSel.lower() == 'q':
                    exit()
                try:
                    numSel = int(numSel)
                    break
                except ValueError:
                    print("The input must be an integer.  Please try again or enter 'q' to exit.")

            print ("First dance?")
            print (" [W]altz")
            print (" [T]ango")
            print (" [V]iennese Waltz")
            print (" [F]oxtrot")
            print (" [Q]uickstep")
            print (" [WCS]")
            print (" [C]ha Cha")
            print (" [S]amba")
            print (" [R]umba")
            print (" [P]aso Doble")
            print (" [J]ive")
            while True:
                firstDance = raw_input("First dance <W/T/V/F/Q/WCS/C/S/R/P/J> or enter 'x' to e[x]it: ")
                firstDance = firstDance.upper().strip()
                if firstDance == 'X':
                    exit()
                elif firstDance not in ('W', 'T', 'V', 'F', 'Q', 'WCS', 'C', 'S', 'R', 'P', 'J'):
                    print("Unrecognized dance selection.  Please try again.")
                else:
                    break
        else:
            numSel = 2
            firstDance = 'W'
        clearScreen()
        play_music(numSel, 0, firstDance, musicLists)

        # Line dance played after first playlist ends
        print
        while True:
            continueYN = raw_input("At end of first playlist.  Play a line dance <Y/N>: ")
            continueYN = continueYN.upper().strip()
            if continueYN not in ('Y', 'N'):
                print "Unrecognized input.  Try again."
            else:
                break
        if continueYN == 'Y':
            play_linedance(musicLists)

        repetitions = 0
        while True:
            print
            while True:
                continueYN = raw_input("Begin another playlist starting with Waltz <Y/N>: ")
                continueYN = continueYN.upper().strip()
                if continueYN not in ('Y', 'N'):
                    print "Unrecognized input.  Try again."
                else:
                    break
            if continueYN == 'Y':
                print
                repetitions = repetitions + 1
                if repetitions < 2:
                    play_music(numSel, repetitions * numSel, 'W', musicLists)
                else:
                    # on 3rd and subsequent passes only play one selection.
                    play_music(1, 2 * numSel + repetitions - 2, 'W', musicLists)
                print
            else:
                raw_input("Enter carriage return to exit program...")
                exit()

    except Exception:
        display_exception()

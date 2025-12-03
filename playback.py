import vlc
import os
import random
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from files import Files
from memory import memory

# Initialise VLC
instance = vlc.Instance("--vout=dummy")
player = instance.media_player_new() # type: ignore


# Handles playback of music files / streaming
class Playback():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When the gui calls this file and its functions, its passing in its whole object reference

    # Handles audio playback based on given parameters
    def recieve_song(self, fp:str, option:str): # fp is songs path, option is what to do with song file
        media = instance.media_new(fp) # type: ignore
        player.set_media(media)
        print("Song recieved")

        if option == "play":
            print("Beginning playback for song ", fp)
            player.play()
            self.progress_bar(fp, player)
            self.gui.update_text(self.get_title_artist(fp))
            self.gui.update_album_art(self.get_album_art())
            memory.set_scroll_direction('left')
            if self.gui.navbar.get() != "Playback":
                print("Switched to Playback tab")
                self.gui.navbar.set("Playback")
            self.gui.update_idletasks()
            self.gui.scrolling_label(True)

    def get_title_artist(self, fp):
        if fp.endswith(".flac"):
            audio = FLAC(fp) # Metadata dictionary
            title = str(audio["TITLE"]).strip("{}[]'")
            artist = str(audio["ARTIST"]).strip("{}[]'")
        elif fp.endswith(".mp3"): 
            audio = MP3(fp)
            title = str(audio["TITLE"]).strip("{}[]'")
            artist = str(audio["ARTIST"]).strip("{}[]'")
        return title, artist

    def get_album_art(self):
        supported_formats = ('.png', '.jpg')
        album_path = memory.get_current_path()
        files = [name for name in os.listdir(album_path) if name.endswith(supported_formats)]
        try:
            art_path = album_path + '/' + files[0]
        except:
            art_path = 'images/stock_album_art_7.jpg'
        return art_path

    def progress_bar(self, fp, player): # fp is still full_path of song (access to metadata), player is song instance
        counter = 1
        # If player stopped or finished, exit loop by NOT calling after() again
        if player.get_state() in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error): # type: ignore
            print("Song finished and stopping loop")
            return
        else:
            if player.get_state() in (vlc.State.Playing, vlc.State.Opening, vlc.State.Buffering): # type: ignore
                self.gui.after(500, lambda: self.progress_bar(fp, player)) # Update bar twice a second
            else:
                self.gui.after(1000, lambda: self.progress_bar(fp, player)) # Update bar once a second
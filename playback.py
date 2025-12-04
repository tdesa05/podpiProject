import vlc
import os
import random
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from files import Files
from memory import memory

# Initialise VLC
instance = vlc.Instance("--vout=dummy")

# Handles playback of music files / streaming
class Playback():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When the gui calls this file and its functions, its passing in its whole object reference
        self.player = instance.media_list_player_new() # type: ignore
        self.media_list = instance.media_list_new() # type: ignore

    def reset_media_list(self):
        self.media_list = instance.media_list_new() # type: ignore

    # Handles audio playback based on given parameters
    def recieve_song(self, fp:str, option:str): # fp is songs path, option is what to do with song file
        print("Song recieved")
        if option == "queue":
            # ADD AN IF TO SEE IF LIST CONTAINS ANY FILES FIRST (SO THE QUEUE BUTTON WORKS EVEN WHEN IT SHOULDNT)
            media = instance.media_new(fp) # type: ignore
            self.media_list.add_media(self.media_list) # Add media to list
            print(fp, "Queued")
            self.player.next() # Skip to next song (REMOVE ONLY FOR DEBUGGING)
        elif option == "play":
            self.player.stop() # Stop playback
            self.reset_media_list()
            media = instance.media_new(fp) # type: ignore
            self.media_list.add_media(media) # Add song
            self.player.set_media_list(self.media_list) # Add song to player

            print("Beginning playback for song ", fp)
            self.player.play() # Play song

            if self.gui.navbar.get() != "Playback":
                print("Switched to Playback tab")
                self.gui.navbar.set("Playback")

        # Statements to run no matter what
        self.progress_bar(fp, self.player)
        self.gui.update_text(self.get_title_artist(fp))
        self.gui.update_album_art(self.get_album_art())
        memory.set_scroll_direction('left')
        self.gui.update_idletasks()
        self.gui.scrolling_label(True)

    # Get artist name from metadata of current song
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

    # Get album art from folder of current song
    def get_album_art(self):
        supported_formats = ('.png', '.jpg')
        album_path = memory.get_current_path()
        files = [name for name in os.listdir(album_path) if name.endswith(supported_formats)]
        try:
            art_path = album_path + '/' + files[0]
        except:
            art_path = 'images/stock_album_art_7.jpg'
        return art_path

    # Visual indicator of remaining song time
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
    
    # Check whether shuffle is enabled or not, then handle queue
    def check_shuffle(self):
        if memory.get_shuffle():
            shuffle = memory.get_shuffle()
            old_list = self.media_list.get_media_list()

            # Extract all media items
            items = [old_list.item_at_index(i) for i in range(old_list.count())]

            # Shuffle in Python
            random.shuffle(items)

            # Create a new media list
            new_list = instance.media_list_new() # type: ignore

            # Add items back
            for m in items:
                new_list.add_media(m)

            # Replace the existing list
            self.reset_media_list()
            self.media_list.set_media_list(new_list)
        else:
            # Un shuffle playback
            print("unshuffle")


    # Shuffle entire library
    def library_shuffle(self,):
        self.reset_media_list()

        # Need to go through library of songs and add them all
        self.media_list.add('')

        # Then shuffle this queue


        self.player.set_media_list(self.media_list)
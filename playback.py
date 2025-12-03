import vlc
import os
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from files import Files
from memory import memory

# Initialise VLC
instance = vlc.Instance("--vout=dummy")
player = instance.media_player_new() # type: ignore
print(player)


# Handles playback of music files / streaming
class Playback():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When the gui calls this file and its functions, its passing in its whole object reference

    # Handles audio playback based on given parameters
    def recieve_song(self, fp:str, option:str): # fp is songs path, option is what to do with song file
        media = instance.media_new(fp) # type: ignore
        player.set_media(media)

        if option == "play":
            if self.gui.navbar.get() != "Playback":
                self.gui.navbar.set("Playback")
            player.play()
            self.progress_bar(fp, player)
            self.get_album_art()
            memory.set_scroll_direction('left')
            self.gui.scrolling_label()

    def get_album_art(self):
        supported_formats = ('.png', '.jpg')
        album_path = memory.get_current_path()
        files = [name for name in os.listdir(album_path) if name.endswith(supported_formats)]
        art_path = album_path + '/' + files[0]
        self.gui.update_album_art(art_path)

    def progress_bar(self, fp, player): # fp is still full_path of song (access to metadata), player is song instance
        counter = 1
        # If player stopped or finished, exit loop by NOT calling after() again
        if player.get_state() in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error): # type: ignore
            print("Song finished and stopping loop")
            return
        else:
            print(player.get_time()/1000)
            if player.get_state() in (vlc.State.Playing, vlc.State.Opening, vlc.State.Buffering): # type: ignore
                self.gui.after(500, lambda: self.progress_bar(fp, player)) # Update bar twice a second
            else:
                print("Waiting")
                self.gui.after(1000, lambda: self.progress_bar(fp, player)) # Update bar once a second
import vlc
import os
import random
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from files import Files
from memory import memory
from urllib.parse import urlparse
from urllib.request import url2pathname

# Initialise VLC
instance = vlc.Instance("--vout=dummy")
player = instance.media_list_player_new() # type: ignore

# Handles playback of music files / streaming
class Playback():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When another file calls this file and its functions, its passing in its whole object reference
        self.media_library = 'MusicLibrary'
        self.media_list = instance.media_list_new() # type: ignore
        self.files = Files(self)

        # Player to read events off of
        self.internal_player = player.get_media_player()

        # Event manager
        player_events = self.internal_player.event_manager()
        player_events.event_attach(vlc.EventType.MediaPlayerPlaying, lambda event: self.on_play(event)) # type: ignore
        #player_events.event_attach(vlc.EventType.MediaPlayerPaused, self.on_pause) # type: ignore
        player_events.event_attach(vlc.EventType.MediaPlayerEndReached, lambda event: self.on_end(event)) # type: ignore
        
        # Load media list stored from last instance
        self.load_media_list()

    def load_media_list(self):
        for fp in memory.song_list:
            media = instance.media_new(fp) # type: ignore
            self.media_list.add_media(media)
            player.set_media_list(self.media_list)
            player.play()
            player.pause()

    def reset_media_list(self):
        self.media_list = instance.media_list_new() # type: ignore

    def song_action(self, action:str):
        if action == 'skip':
            player.next()
        elif action == 'pause' or 'play':
            if vlc.State.Playing: # type: ignore
                player.pause()
            elif vlc.State.Paused: # type: ignore
                player.play()
        elif action == 'back':
            player.previous()
        elif action == 'shuffle':
            self.library_shuffle(self.media_library, False)



    # Handles audio playback based on given parameters
    def recieve_song(self, fp:str = "", option:str = "play"): # fp is songs path, option is what to do with song file
        # Save last played song
        memory.song_list.clear()
        memory.previous_song = memory.current_song
        memory.save()
        print("Song recieved")
        if option == "queue":
            # ADD AN IF TO SEE IF LIST CONTAINS ANY FILES FIRST (SO THE QUEUE BUTTON WORKS EVEN WHEN IT SHOULDNT)
            memory.song_list.append(fp)
            media = instance.media_new(fp) # type: ignore
            self.media_list.add_media(media) # Add media to list
            print(fp, "Queued")
        elif option == "play":
            if fp.startswith('file:'):
                print("butt")
            else:
                songs = []
                song_index = None
                player.stop() # Stop playback
                self.reset_media_list()

                # Find all songs in directory
                for root, dirs, files in os.walk(memory.current_path):
                    for file in files:
                        if file.lower().endswith(('.mp3', '.flac')):
                            full_path = os.path.join(root, file)
                            songs.append(full_path)
                
                songs.sort()
                
                # Create list from songs within directory
                for index, full_path in enumerate(songs):
                    if full_path == fp:
                        song_index = index
                    media = instance.media_new(full_path) # type: ignore
                    self.media_list.add_media(media) # Add song
                    memory.song_list.append(full_path)

                player.set_media_list(self.media_list) # Add song to player
                
                print("Beginning playback for song ", fp)

                # Start playback from chosen song
                if player.play_item_at_index(song_index) == 0: # 0 on success, -1 on failure
                    print(f"Skipped to index {song_index} (Success)")
                else:
                    print(f"Failed to skip to index {song_index}")
                if self.gui.navbar.get() != "Playback":
                    print("Switched to Playback tab")
                    self.gui.navbar.set("Playback")
        memory.save()


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
        album_path = os.path.dirname(memory.current_song)
        files = [name for name in os.listdir(album_path) if name.endswith(supported_formats)]
        try:
            art_path = album_path + '/' + files[0]
        except:
            art_path = 'images/stock_album_art_2.jpg'
        return art_path

    # Visual indicator of remaining song time
    def progress_bar(self, fp): # fp is still full_path of song (access to metadata), player is song instance
        # If player stopped or finished, exit loop by NOT calling after() again
        if player.get_state() in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error): # type: ignore
            print("Song finished and stopping loop")
            return
        else: 
            if player.is_playing(): # type: ignore
                m = player.get_media_player() # Media player within listplayer
                current_time = m.get_time()
                length = m.get_length()
                self.gui.update_progress_bar(current_time, length)
                self.gui.after(500, lambda: self.progress_bar(fp)) # Update bar twice a second
            elif player.get_state() == vlc.State.Paused: # type: ignore
                self.gui.after(1000, lambda: self.progress_bar(fp)) # Update bar once a second
    
    # Check whether shuffle is enabled or not, then handle queue
    def check_shuffle(self):
        if memory.shuffle:
            print("Shuffled")
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
            self.media_list.set_media(new_list)
            memory.shuffle = False
        else:
            # Un shuffle playback
            print("Unshuffled")

            memory.shuffle = True
        memory.save

    # Events for on_play NEED TO FIX FOR PICKING SONG
    def on_play(self, event): # 'event' required for the lambda, VLC doesn't like class functions
        mrl = player.get_media_player().get_media().get_mrl()
        fp = url2pathname(urlparse(mrl).path)
        if memory.current_song == fp:
            return
        else:
            memory.current_song = fp
            print(fp)
            #self.shuffle(self.media_library, False)
            # Statements to run no matter what
            self.progress_bar(fp)
            self.gui.update_text(self.get_title_artist(fp))
            self.gui.update_album_art(self.get_album_art())
            memory.scroll_direction = 'left'
            self.gui.update_idletasks()
            self.gui.scrolling_label(True)
        memory.save()

    def volume(self, increment:int):
        current_volume = player.audio_get_volume()
        new_volume = current_volume + increment

        if (new_volume) > 100 or (new_volume) < 0:
            new_volume = current_volume
            print(f"Volume at upper/lower limit")

        memory.volume_lvl = new_volume
        player.audio_set_volume(new_volume)
        memory.save()
    
    def on_pause(self, event):
        pass

    def on_end(self, event):
        memory.previous_song = memory.current_song
        print(memory.previous_song)
        memory.save()

    # Shuffle a folder of music
    def library_shuffle(self, folder, queue:bool):
        songs = []
        # Search (root library)
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(('.mp3', '.flac')):
                    full_path = os.path.join(root, file)
                    songs.append(full_path)
        
        if not songs:
            print("No songs found in library!")
            return

        random.shuffle(songs)

        # Create new media list, add each song from songs list to it
        new_media_list = instance.media_list_new() # type: ignore
        for fp in songs:
            media = instance.media_new(fp) # type: ignore
            new_media_list.add_media(media)

        if queue:
            # Add each media item to end of current playback if in queue
            for i in range(new_media_list.count()):
                self.media_list.add_media(new_media_list.item_at_index(i))
        else:
            player.stop()
            self.reset_media_list()
            self.media_list = new_media_list
            player.set_media_list(self.media_list)
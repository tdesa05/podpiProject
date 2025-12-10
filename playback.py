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
            self.shuffle(self.media_library, False)



    # Handles audio playback based on given parameters
    def recieve_song(self, fp:str = "", option:str = "play"): # fp is songs path, option is what to do with song file
        print("Song recieved")
        if option == "queue":
            # ADD AN IF TO SEE IF LIST CONTAINS ANY FILES FIRST (SO THE QUEUE BUTTON WORKS EVEN WHEN IT SHOULDNT)
            media = instance.media_new(fp) # type: ignore
            self.media_list.add_media(self.media_list) # Add media to list
            print(fp, "Queued")
            player.next() # Skip to next song (REMOVE ONLY FOR DEBUGGING)
        elif option == "play":
            if fp.startswith('file:'):
                print("butt")
            else:
                player.stop() # Stop playback
                self.reset_media_list()
                media = instance.media_new(fp) # type: ignore
                self.media_list.add_media(media) # Add song
                player.set_media_list(self.media_list) # Add song to player

                print("Beginning playback for song ", fp)
                player.play() # Play song
                if self.gui.navbar.get() != "Playback":
                    print("Switched to Playback tab")
                    self.gui.navbar.set("Playback")


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
        album_path = os.path.dirname(memory.get_current_song())
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
            self.media_list.set_media(new_list)
        else:
            # Un shuffle playback
            print("unshuffle")

    # Events for on_play NEED TO FIX FOR PICKING SONG
    def on_play(self, event): # 'event' required for the lambda, VLC doesn't like class functions
        print("act")
        mrl = player.get_media_player().get_media().get_mrl()
        fp = url2pathname(urlparse(mrl).path)
        if memory.get_current_song == fp:
            return
        else:
            memory.set_current_song(fp)
            print(fp)
            #self.shuffle(self.media_library, False)
            # Statements to run no matter what
            self.progress_bar(fp)
            self.gui.update_text(self.get_title_artist(fp))
            self.gui.update_album_art(self.get_album_art())
            memory.set_scroll_direction('left')
            self.gui.update_idletasks()
            self.gui.scrolling_label(True)

    def on_pause(self, event):
        pass

    def on_end(self, event):
        memory.set_previous_song(memory.get_previous_song())
        print(memory.get_previous_song)

    # Shuffle a folder of music
    def shuffle(self, folder, queue:bool):
        # Beginning of search (root library)
        root_info = self.files.iterate_files(folder)
        root_contents = root_info[0] # Index 0 is contents list, index 1 is path to directory
        root_directory = root_info[1]
        initial_fetch = self.files.fetch_songs(root_contents, root_directory)

        songs:list = initial_fetch[0]
        continue_fetch = initial_fetch[1]
        directories:list = initial_fetch[2]
        new_directories:list = []

        # Go into each directory until getting each songs
        while continue_fetch:
            for i in directories:
                folder_info = self.files.iterate_files(i)
                folder_contents = folder_info[0]
                folder_directory = folder_info[1]
                fetch = self.files.fetch_songs(folder_contents, folder_directory)
                found_songs = fetch[0]
                songs += found_songs
                continue_fetch = fetch[1]
                found_directories = fetch[2]
                new_directories += found_directories
            # Once all folders in directory are searched, update to new folders 
            directories.clear()
            directories += new_directories
            new_directories.clear()


        # Then shuffle this list of songs
        random.shuffle(songs)

        # Set media list
        new_media_list = instance.media_list_new() # type: ignore
        for fp in songs:
            media = instance.media_new(fp) # type: ignore
            new_media_list.add_media(media)
        
        if queue: # Allows control whether to skip to shuffle queue or let current song playout
            for i in range(new_media_list.count()):
                self.media_list.add_media(new_media_list.item_at_index(i))
        else:
            player.stop()
            self.reset_media_list()
            self.media_list = new_media_list
            player.set_media_list(self.media_list)
            player.play()
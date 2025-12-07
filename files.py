import os
from mutagen.flac import FLAC
from mutagen.mp3 import MP3

# Handles interpretation and organising of files
class Files():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When another file calls this file and its functions, its passing in its whole object reference
        self.root = "MusicLibrary" # Root music directory

    # Iterates through given folder and returns list of contents
    def iterate_files(self, folder): # Folder containing music files
        supported_formats = ('.mp3', '.flac')  # Supported audio formats
        files = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name)) or name.endswith(supported_formats)]
        files.sort() # Maintain folder order
        abspath = os.path.abspath(folder)
        relpath = abspath.split(self.root, 1)[1]
        relpath = self.root + relpath
        return files, relpath

    def check_directory(self, i, f, full_path):
        pos = i # If a folder, row position will just be order folder is read
        title = f # If a folder, use default title

        # Handle whether file is folder (go into directory) or if audio (play in VLC)
        if f.endswith(".flac") or f.endswith(".mp3"):
            if f.endswith(".flac"):
                audio = FLAC(full_path) # Metadata dictionary
                pos = i
                title = str(audio["TITLE"]).strip("{}[]'")
                song = True
            else: 
                audio = MP3(full_path)
                pos = i
                title = str(audio["TITLE"]).strip("{}[]'")
                song = True
        else:
           song = False
        return pos, title, song # Position to be placed, metadata title, song or directory (True/False)
        
    # Searches folder for songs and directories, returns these songs, whether more searching is required and the directories to search
    def fetch_songs(self, folder_contents:list, folder_directory:str):
        new_folder_contents:list = [] # Contains new items
        directories:list = [] # Contains directories that need to be searched
        continue_fetch = False # Default - indicates no more searching required

        # Go through folder contents, add to list if is music file
        for i in folder_contents:
            if str(i).endswith('.flac' or '.mp3'): # Check if song
                if i in new_folder_contents: # No duplicates
                    pass
                else:
                    new_folder_contents.insert(0, folder_directory + '/' + i) # Insert song
            else:
                if not continue_fetch:
                    continue_fetch = True
                directories.insert(0, folder_directory + '/' + i)

            # Sorting, just to be neat
            directories.sort()
            new_folder_contents.sort()
        
        return new_folder_contents, continue_fetch, directories
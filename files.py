import os
from mutagen.flac import FLAC
from mutagen.mp3 import MP3

# Handles interpretation and organising of files
class Files():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When the gui calls this file and its functions, its passing in its whole object reference
        self.root = "MusicLibrary" # Root music directory

    # Iterates through given folder and returns list of contents
    def iterate_files(self, folder): # Folder containing music files
        supported_formats = ('.mp3', '.flac')  # Supported audio formats
        files = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name)) or name.endswith(supported_formats)]
        #print(files)
        return files, os.path.abspath(folder)

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
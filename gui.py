from tkinter import *
import customtkinter as ctk
import subprocess
import os
import time
import vlc
from mutagen.flac import FLAC
from mutagen.mp3 import MP3

# Set appearance and theme
ctk.set_appearance_mode("dark")
#customtkinter.set_default_color_theme("dark-blue")

# Colours
titleBlack = "#a8a8a8"
titleBlack = "#161617"

bodyGrey = "#f5f2f2"
bodyBlack = "#221f24"

highlightBlue = "#2394fc"
highlightPurple = "#7402de"

# Initialise VLC
instance = vlc.Instance("--vout=dummy")
player = instance.media_player_new() # type: ignore
print(player)




class Selection():
    def __init__(self):
        super().__init__()
        self.selection = None
    
    # Getter method
    def get(self):
        return self.selection

    # Setter method
    def set(self, selection):
        self.selection = selection



class Navigation(ctk.CTk):
    # Initialize the main window
    def __init__(self):
        super().__init__()
        self.title("Navigate Library") # Title of the window
        self.geometry("320x240") # Width x Height
        self.configure(fg_color = titleBlack, bg_color = titleBlack)

        # Fonts
        self.title_font = ctk.CTkFont(family = "Myriad", size = 12, weight = "bold")
        self.body_font = ctk.CTkFont(family = "Myriad", size = 16, weight = "bold")

        # Navigation bar, view control
        self.navbar = ctk.CTkTabview(self,
                                     anchor = "s",
                                     corner_radius = 0,
                                     width = 320,
                                     height = 15,
                                     fg_color = bodyBlack,
                                     bg_color = bodyBlack,
                                     segmented_button_fg_color = bodyBlack,
                                     segmented_button_unselected_color = bodyBlack,
                                     segmented_button_selected_color = highlightPurple
                                     )
        self.navbar.pack()

        # Initialise tabs
        self.fileTab = self.navbar.add("Files")
        self.playbackTab = self.navbar.add("Playback")

        # Stylise navbar
        self.navbar._segmented_button.configure(
            corner_radius = 10,
            text_color = "white",
            font = self.title_font
        )

        # Tab title
        self.title_label = ctk.CTkLabel(self.fileTab,
                                        width = 320,
                                        height = 20,
                                        text = " Music",
                                        text_color = "white",
                                        font = self.title_font,
                                        fg_color = titleBlack,
                                        corner_radius = 0,
                                        compound = "left",
                                        anchor = "w"
                                        )
        self.title_label.pack()

        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.fileTab,
                                                    orientation ="vertical",
                                                    width = 320,
                                                    height = 240,
                                                    fg_color = "transparent",
                                                    scrollbar_button_color = titleBlack,
                                                    border_width = 0,
                                                    corner_radius = 0
                                                )
        self.scrollable_frame.pack()
        self.scrollable_frame.grid_columnconfigure(0, weight = 1)
        self.scrollable_frame.grid_rowconfigure(0, weight = 1)

        # Tab title
        self.title_label = ctk.CTkLabel(self.playbackTab,
                                        width = 320,
                                        height = 20,
                                        text = " Playback",
                                        text_color = "white",
                                        font = self.title_font,
                                        fg_color = titleBlack,
                                        corner_radius = 0,
                                        compound = "left",
                                        anchor = "w"
                                        )
        self.title_label.pack()

        # Create playback frame
        self.frame = ctk.CTkFrame(self.playbackTab,
                                width = 320,
                                height = 240,
                                fg_color = "transparent",
                                border_width = 0,
                                corner_radius = 0
                            )
        self.frame.pack()


        # Initialise widgets
        self.add_to_frame("MusicLibrary")
    
    # Handles audio playback based on given parameters
    def playback(self, fp:str, option:str, navigate:bool):
        media = instance.media_new(fp) # type: ignore
        player.set_media(media)
        if navigate:
            print("Switched to playback screen")
            self.navbar.set("Playback")
        if option == "play":
            player.play()

    # Iterates through given folder and returns list of contents
    def iterate_files(self, folder):
        folder = folder  # Folder containing music files
        supported_formats = ('.mp3', '.flac')  # Supported audio formats
        files = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name)) or name.endswith(".flac") or name.endswith(".mp3")]
        #print(files)
        return files, os.path.abspath(folder)
    
    # Clear the scrollable frame
    def clear_frame(self):
        for item in self.scrollable_frame.winfo_children():
            item.destroy()

    # Add items to scrollable frame
    def add_to_frame(self, folder):
        self.clear_frame()
        files = self.iterate_files(folder) # List, contains files, and path of directory
        print(files[1])
        
        # Iterate through files in directory
        for i, f in enumerate(files[0]):
            pos = i # If a folder, row position will just be order folder is read
            title = f # If a folder, use default title

            # Path of file
            full_path = files[1] + '/' + f

            # Handle whether file is folder (go into directory) or if audio (play in VLC)
            if f.endswith(".flac") or f.endswith(".mp3"):
                if f.endswith(".flac"):
                    audio = FLAC(full_path) # Metadata dictionary
                    pos = i
                    title = str(audio["TITLE"]).strip("{}[]'")
                else: 
                    audio = MP3(full_path)
                    pos = i
                    title = str(audio["TITLE"]).strip("{}[]'")
                command = lambda fp = full_path: self.playback(fp, "play", True)
            else:
                command = lambda fp = full_path: self.add_to_frame(fp)

            print(f)
            entry = ctk.CTkButton(self.scrollable_frame,
                                    width = 320, 
                                    height = 8, 
                                    fg_color = "transparent",
                                    hover_color = highlightPurple,
                                    text = title,
                                    text_color = "white",
                                    font = self.body_font,
                                    corner_radius = 0,
                                    border_width = 0,
                                    border_color = "white",
                                    anchor = "w",
                                    command = command # Refers to previously created lambda function (play or add to frame)
                                    )
            entry.grid(row=pos, column=1, pady=0, padx=2, sticky="ew")
    # Sets scope for clickwheel, handles which item to be highlighted, ready for selection
    def cw_handler(self, items):
        cw_range = len(items)

# Run the application
if __name__ == "__main__":
    navigation = Navigation()
    navigation.mainloop()
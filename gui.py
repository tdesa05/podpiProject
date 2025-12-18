
import tkinter
import customtkinter as ctk
import time
from PIL import Image
# Local files
from controls import Controls
from memory import memory
from playback import Playback
from files import Files
#from spotify import Spotify


# Set appearance and theme
ctk.set_appearance_mode("dark")
#customtkinter.set_default_color_theme("dark-blue")

# Colours
titleBlack = "#a8a8a8"
titleBlack = "#161617"

bodyGrey = "#f5f2f2"
bodyBlack = "#221f24"

# Hover colours / signifies selected
highlightBlue = "#2394fc"
highlightPurple = "#7402de"

# Stock album art prior to choosing any song
albumArtPH = ctk.CTkImage(dark_image = Image.open("images/summertime_lovin.jpg"),
                            size = (120, 120))

# Contains all graphical handling/functions
class Gui(ctk.CTk):
    # Initialize the main window
    def __init__(self):
        super().__init__()
        self.title("Navigate Library") # Title of the window
        self.geometry("320x240") # Width x Height
        self.resizable(False, False)
        self.configure(fg_color = titleBlack, bg_color = titleBlack)

        # Classes (logic)
        self.playback = Playback(self)
        self.controls = Controls(self, self.playback)
        self.files = Files(self)

        # Jobs (running processes)
        self.scroll_job = None

        # Widgets
        self.song_widgets = []

        # Bind controls
        self.bind('<Key>', self.controls.keyboard_input)

        # Fonts
        self.title_font = ctk.CTkFont(family = "Myriad", size = 12, weight = "bold")
        self.body_font = ctk.CTkFont(family = "Myriad", size = 16, weight = "bold")
        self.time_font = ctk.CTkFont(family="Courier New", size=12) # All characters are same size

        # Navigation bar, view control
        self.navbar = ctk.CTkTabview(self,
                                     anchor = "s",
                                     corner_radius = 0,
                                     width = 320,
                                     height = 10,
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
        self.spotifyTab = self.navbar.add("Spotify")



        # Stylise navbar
        self.navbar._segmented_button.configure(
            corner_radius = 10,
            text_color = "white",
            font = self.title_font
        )

        ### FILES TAB ###
        # Tab title
        self.file_title_label = ctk.CTkLabel(self.fileTab,
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
        self.file_title_label.pack()

        # Create scrollable frame
        self.files_scrollable_frame = ctk.CTkScrollableFrame(self.fileTab,
                                                    orientation ="vertical",
                                                    width = 320,
                                                    height = 240,
                                                    fg_color = "transparent",
                                                    scrollbar_button_color = titleBlack,
                                                    border_width = 0,
                                                    corner_radius = 0
                                                )
        self.files_scrollable_frame.pack()
        self.files_scrollable_frame.grid_columnconfigure(0, weight = 1)
        self.files_scrollable_frame.grid_rowconfigure(0, weight = 1)


        ### PLAYBACK TAB ###
        # Tab title
        self.playback_title_label = ctk.CTkLabel(self.playbackTab,
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
        self.playback_title_label.pack()

        # Create playback frame
        self.playback_frame = ctk.CTkFrame(self.playbackTab,
                                width = 320,
                                height = 240,
                                fg_color = "transparent",
                                border_width = 0,
                                corner_radius = 0
        )
        self.playback_frame.pack()

        # Song album art
        self.album_art = ctk.CTkLabel(self.playback_frame,
                                     width = 120,
                                     height = 120,
                                     image = albumArtPH,
                                     text = ""
        )
        self.album_art.pack(padx = 5, pady = 5)

        # Song title frame
        self.song_title_frame = ctk.CTkFrame(self.playback_frame,
                                             width = 250, # Width of viewable text
                                             height = 20,
                                             bg_color = 'transparent',
                                             fg_color = 'transparent'
        )
        self.song_title_frame.pack(padx = 5, pady = 0)

        # Song title
        self.song_title = ctk.CTkLabel(self.song_title_frame,
                                      height = 20,
                                      text = "Summertime Lovin'",
                                      font = self.body_font
        )
        self.song_title.place(x = 250/2, y = 20/2, anchor = 'center')

        # Artist name
        self.song_artist = ctk.CTkLabel(self.playback_frame,
                                      width = 70,
                                      height = 20,
                                      text = "Solid Bold",
                                      font = self.title_font              
        )
        self.song_artist.pack(padx = 5, pady = 0)

        # Frame containing bar, and labels
        self.progress_frame = ctk.CTkFrame(self.playback_frame,
                                           height = 10,
                                           fg_color = "transparent"
        )   
        self.progress_frame.pack(fill = "x", padx = 0)

        # Current song positon
        self.progress_current = ctk.CTkLabel(self.progress_frame,
                                           width = 20,
                                           height = 10,
                                           font = self.time_font,
                                           text = "0:00",
                                           anchor = "w"
        )
        self.progress_current.pack(padx = 1, side = "left")

        # Progress of song
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame,
                                               width = 200,
                                               height = 10,
                                               progress_color = highlightPurple,
                                               mode = "determinate"
        )
        self.progress_bar.pack(side = "left", padx = 5, pady = 0)

        # Length of song
        self.progress_end = ctk.CTkLabel(self.progress_frame,
                                           width = 20,
                                           height = 10,
                                           font = self.time_font,
                                           text = "10:00",
                                           anchor = "e"
        )
        self.progress_end.pack(padx = 1, side = "right")


        ### SPOTIFY TAB ###
        # Tab title
        self.spotify_title_label = ctk.CTkLabel(self.spotifyTab,
                                        width = 320,
                                        height = 20,
                                        text = " Spotify",
                                        text_color = "white",
                                        font = self.title_font,
                                        fg_color = titleBlack,
                                        corner_radius = 0,
                                        compound = "left",
                                        anchor = "w"
        )
        self.spotify_title_label.pack()

        # Create scrollable frame
        self.spotify_scrollable_frame = ctk.CTkScrollableFrame(self.spotifyTab,
                                                    orientation ="vertical",
                                                    width = 320,
                                                    height = 240,
                                                    fg_color = "transparent",
                                                    scrollbar_button_color = titleBlack,
                                                    border_width = 0,
                                                    corner_radius = 0
                                                )
        self.spotify_scrollable_frame.pack()
        self.spotify_scrollable_frame.grid_columnconfigure(0, weight = 1)
        self.spotify_scrollable_frame.grid_rowconfigure(0, weight = 1)

        # Initialise widgets
        self.add_to_frame("MusicLibrary")

    # Clear the scrollable frame
    def clear_frame(self):
        for item in self.files_scrollable_frame.winfo_children():
            item.destroy()
        self.files_scrollable_frame._parent_canvas.yview_moveto(0.0) # Reset scroll position to top of page

    # Add items to scrollable frame
    def add_to_frame(self, folder):
        self.song_widgets.clear()
        self.clear_frame()
        files = self.files.iterate_files(folder) # Tuple (List of files, directory)
        memory.current_path = files[1]
        # Iterate through files in directory
        for i, f in enumerate(files[0]):
            # Path of file
            full_path = files[1] + '/' + f
            memory.current_song = files[0][i]
            # Interpret files
            file_info = self.files.check_directory(f, full_path)
            # Song or directory
            if file_info[1]:
                command = lambda fp = full_path: self.playback.recieve_song(fp, "play")
            else:
                command = lambda fp = full_path: self.add_to_frame(fp) 

            # Create buttons for directories/files
            entry = ctk.CTkButton(self.files_scrollable_frame,
                                    width = 320, 
                                    height = 8, 
                                    fg_color = "transparent",
                                    text = file_info[0],
                                    text_color = "white",
                                    font = self.body_font,
                                    corner_radius = 0,
                                    border_width = 0,
                                    border_color = "white",
                                    anchor = "w",
                                    hover = False,
                                    command = command   # Refers to previously created lambda function (play or add to frame)
                                    )
            entry.grid(column=1, pady=0, padx=2, sticky="ew")
            self.song_widgets.append(entry)
        try:
            memory.selected = [0, self.song_widgets[0].cget("text")]
        except Exception as e:
            print(f"Failed to initialise memory.selected: {e}")

    # Updates image to album art of current directory
    def update_album_art(self, art_path):
        new_art = ctk.CTkImage(dark_image = Image.open(art_path),
                               size = (120, 120)
                               )
        self.album_art.configure(image = new_art)

    # Updates text on playback screen
    def update_text(self, info):
        title = info[0]
        artist = info[1]
        self.song_title.configure(text = title)
        self.song_artist.configure(text = artist)

    # Updates gui to reflect progress of song, along with timestamps on bar
    def update_progress_bar(self, current_time, total_time):
        if current_time > 0:
            bar_pos = current_time/total_time
        else:
            bar_pos = 0
        self.progress_bar.set(bar_pos)

        # String for current song time
        current_time = (current_time / 1000)
        current_minutes = int(current_time // 60)
        current_seconds = int(current_time % 60)
        s_current_seconds = str(current_seconds)
        if len(s_current_seconds) == 1:
            s_current_seconds = '0' + s_current_seconds
        str_current = str(current_minutes) + ':' + s_current_seconds

        # String for length of song
        total_time = (total_time / 1000)
        total_minutes = int(total_time // 60)
        total_seconds = int(total_time % 60)
        s_total_seconds = str(total_seconds)
        if len(s_total_seconds) == 1:
            s_total_seconds = '0' + s_total_seconds
        str_length = str(total_minutes) + ':' + s_total_seconds

        if self.progress_end.cget("text") != str_length:
            self.progress_end.configure(text = str_length)
        self.progress_current.configure(text = str_current)
    

    # In the event a song title does not fit on screen, scroll left and right to fit
    def scrolling_label(self, reset = False):
        text_width = self.song_title.winfo_width()
        frame_width = self.song_title_frame.winfo_width()
        scroll_direction = memory.scroll_direction
        x = memory.scroll_x

        if reset and self.scroll_job != None:
            self.after_cancel(self.scroll_job) # Scroll job ensures only on 'after' is active
            self.scroll_job = None
            self.song_title.place(x = 250/2, y = 20/2, anchor = 'center')
            memory.scroll_x = 0


        # When to change direction 
        end_target = -(text_width - frame_width)
        start_target = 0

        # If text fits into the frame then dont run
        if text_width <= 250: 
            self.song_title.place(x = 250/2, y = 20/2, anchor = 'center')
        
        # Scroll text left
        else:
            if scroll_direction == 'left':
                x -= 0.5
                self.song_title.place(x = x, y = 20/2, anchor = 'w')
                memory.scroll_x = x
                if x <= end_target: # Reverse direction when second half of title shown
                    memory.scroll_direction = 'right'
                    self.scroll_job = self.after(1500, lambda: self.scrolling_label())
                    return

            # Scroll text right
            elif scroll_direction == 'right':
                x += 0.5
                self.song_title.place(x = x, y = 20/2, anchor = 'w')
                memory.scroll_x = x
                if x >= start_target:
                    memory.scroll_direction = 'left'
                    self.scroll_job = self.after(1500, lambda: self.scrolling_label())
                    return # Otherwise speeds up crazy
            self.scroll_job = self.after(24, lambda: self.scrolling_label())

    # Updates gui dependent on user's current location and input, only reads if positive or negative diff from wheel
    def cw_interaction(self, diff):
        tab = self.navbar.get() # We do this here, as would cause issues calling in controls.py as it runs on another thread

        if tab == "Playback":
            if diff > 0:
                self.playback.volume(1)
                # Add volume bar or that appears of side of screen (or make progress bar show volume whilst active?)
            else:
                self.playback.volume(-1)

        elif tab == "Files":
            # If no songs in directory, return
            if not self.song_widgets:
                return
            
            list_len = len(self.song_widgets)

            if memory.selected is None or not memory.selected:
                memory.selected = [0, self.song_widgets[0].cget("text")]
                # Highlight the first one immediately
                self.song_widgets[0].configure(fg_color=(highlightPurple))

            # NAVIGATION 
            current_index = memory.selected[0]
            new_index = current_index

            # Calculate where we WANT to go
            if diff > 0:
                new_index += 1
            elif diff < 0:
                new_index -= 1

            # Check if the new index is actually valid (inside the list)
            if 0 <= new_index < len(self.song_widgets):
                
                # Un-highlight the OLD widget
                # (Reset color to transparent or default)
                self.song_widgets[current_index].configure(fg_color="transparent") 

                # Update Memory
                song_name = self.song_widgets[new_index].cget("text")
                memory.selected = [new_index, song_name]
                print(f"Selected: {song_name}")

                # Highlight the NEW widget
                # (Set color to 'Highlight' color)
                self.song_widgets[new_index].configure(fg_color=(highlightPurple))
                
                # Scroll the view to the new button so it doesn't go off screen
                self.song_widgets[new_index].focus_set()

                # Length of list
                list_len = len(self.song_widgets)

                # Scroll position for pos
                safe_index = max(0, new_index - 3) # Index for scroll to be alligned too, so scroll lags behind selection
                scroll_position = safe_index / list_len

                # 0.0 --> 1.0 is the range
                self.files_scrollable_frame._parent_canvas.yview_moveto(scroll_position)
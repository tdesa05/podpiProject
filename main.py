import tkinter
import customtkinter as ctk
import time
# Local files
from controls import Controls
from memory import memory
from playback import Playback
from files import Files
from PIL import Image

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
albumArtPH = ctk.CTkImage(dark_image = Image.open("images/summertime_lovin.jpg"),
                            size = (120, 120))

# Contains all graphical handling/functions
class Gui(ctk.CTk):
    # Initialize the main window
    def __init__(self):
        super().__init__()
        self.title("Navigate Library") # Title of the window
        self.geometry("320x240") # Width x Height
        self.configure(fg_color = titleBlack, bg_color = titleBlack)

        # Classes (logic)
        self.controls = Controls(self)
        self.playback = Playback(self)
        self.files = Files(self)

        # Jobs (running processes)
        self.scroll_job = None

        # Bind controls
        self.bind('<Key>', self.controls.recieve_input)

        # Fonts
        self.title_font = ctk.CTkFont(family = "Myriad", size = 12, weight = "bold")
        self.body_font = ctk.CTkFont(family = "Myriad", size = 16, weight = "bold")

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

        # Song album art
        self.album_art = ctk.CTkLabel(self.frame,
                                     width = 120,
                                     height = 120,
                                     image = albumArtPH,
                                     text = ""
        )
        self.album_art.pack(padx = 5, pady = 5)

        # Song title frame
        self.song_title_frame = ctk.CTkFrame(self.frame,
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
        self.song_artist = ctk.CTkLabel(self.frame,
                                      width = 70,
                                      height = 20,
                                      text = "Solid Bold",
                                      font = self.title_font              
        )
        self.song_artist.pack(padx = 5, pady = 0)

        # Progress of song
        self.progress_bar = ctk.CTkProgressBar(self.frame,
                                              width = 200,
                                              height = 10
        )
        self.progress_bar.pack(padx = 5, pady = 0)

        # Initialise widgets
        self.add_to_frame("MusicLibrary")
    
    # Clear the scrollable frame
    def clear_frame(self):
        for item in self.scrollable_frame.winfo_children():
            item.destroy()
        self.scrollable_frame._parent_canvas.yview_moveto(0.0) # Reset scroll position to top of page

    # Add items to scrollable frame
    def add_to_frame(self, folder):
        self.clear_frame()
        files = self.files.iterate_files(folder) # Tuple (List of files, directory)
        memory.set_current_path(files[1])
        # Iterate through files in directory
        for i, f in enumerate(files[0]):
            # Path of file
            full_path = files[1] + '/' + f
            memory.set_current_song(files[0][i])
            # Interpret files
            file_info = self.files.check_directory(i, f, full_path)
            # Song or directory
            if file_info[2]:
                command = lambda fp = full_path: self.playback.recieve_song(fp, "play")
            else:
                command = lambda fp = full_path: self.add_to_frame(fp) 

            # Create buttons for directories/files
            entry = ctk.CTkButton(self.scrollable_frame,
                                    width = 320, 
                                    height = 8, 
                                    fg_color = "transparent",
                                    hover_color = highlightPurple,
                                    text = file_info[1],
                                    text_color = "white",
                                    font = self.body_font,
                                    corner_radius = 0,
                                    border_width = 0,
                                    border_color = "white",
                                    anchor = "w",
                                    command = command   # Refers to previously created lambda function (play or add to frame)
                                    )
            entry.grid(row=file_info[0], column=1, pady=0, padx=2, sticky="ew")

    # Updates image to album art of current directory
    def update_album_art(self, art_path):
        new_art = ctk.CTkImage(dark_image = Image.open(art_path),
                               size = (120, 120)
                               )
        self.album_art.configure(image = new_art)

    def update_text(self, info):
        title = info[0]
        artist = info[1]
        self.song_title.configure(text = title)
        self.song_artist.configure(text = artist)

    # In the event a song title does not fit on screen, scroll left and right to fit
    def scrolling_label(self, reset = False):
        text_width = self.song_title.winfo_width()
        frame_width = self.song_title_frame.winfo_width()
        scroll_direction = memory.get_scroll_direction()
        x = memory.get_scroll_x()

        if reset and self.scroll_job != None:
            self.after_cancel(self.scroll_job) # Scroll job ensures only on 'after' is active
            self.scroll_job = None
            self.song_title.place(x = 250/2, y = 20/2, anchor = 'center')
            memory.set_scroll_x(0)


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
                memory.set_scroll_x(x)
                if x <= end_target: # Reverse direction when second half of title shown
                    memory.set_scroll_direction('right')
                    self.scroll_job = self.after(1500, lambda: self.scrolling_label())
                    return

            # Scroll text right
            elif scroll_direction == 'right':
                x += 0.5
                self.song_title.place(x = x, y = 20/2, anchor = 'w')
                memory.set_scroll_x(x)
                if x >= start_target:
                    memory.set_scroll_direction('left')
                    self.scroll_job = self.after(1500, lambda: self.scrolling_label())
                    return # Otherwise speeds up crazy
            self.scroll_job = self.after(24, lambda: self.scrolling_label())


# Run the application
if __name__ == "__main__":
    gui = Gui()
    gui.mainloop()
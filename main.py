import customtkinter as ctk
from gui import Gui
from controls import Controls
from memory import memory
from playback import Playback
from files import Files
from spotify import Spotify


# Run the application
if __name__ == "__main__":
    gui = Gui()
    playback = Playback(gui)
    controls = Controls(gui, playback)
    files = Files(gui)
    spotify = Spotify(gui)

    gui.mainloop()

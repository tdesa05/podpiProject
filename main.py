import customtkinter as ctk
import threading
from gui import Gui
from controls import Controls
from memory import memory
from playback import Playback
from files import Files
#from spotify import Spotify


# Run the application
if __name__ == "__main__":
    gui = Gui()
    memory = memory
    playback = Playback(gui)
    controls = Controls(gui, playback)
    files = Files(gui)
    #spotify = Spotify(gui)

    # 1. Prepare the thread
    # target=controls.cw_handler tells it which function to run
    # daemon=True ensures this thread dies automatically when you close the GUI window
    cw_thread = threading.Thread(target=controls.cw_handler, daemon=True)
    
    # 2. Start the thread (This runs in the background immediately)
    cw_thread.start()

    gui.mainloop()

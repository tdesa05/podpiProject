from memory import memory
from playback import Playback

# Interprets controls based on signals from main.py
class Controls():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When the gui calls this file and its functions, its passing in its whole object reference
        self.playback = Playback(self)

    # Recieve and interpret input (eventually used for physical buttons)
    def recieve_input(self, event):
        print(event.keysym)
        if event.keysym == 'BackSpace':
            if self.gui.navbar.get() == 'Files':
                old_path = memory.get_current_path()
                if old_path.endswith('/MusicLibrary'):
                    return
                else:
                    new_path = old_path.rsplit("/", 1)[0]
                    memory.set_current_path(new_path)
                    self.gui.add_to_frame(new_path)
            else:
                pass
        elif event.keysym == 'q':
            shuffle = memory.get_shuffle()
            if shuffle:
                shuffle = False
            else:
                shuffle = True
            self.playback.check_shuffle()
        elif event.keysym == 'a':
            print()
        elif event.keysym == 'z':
            print()
            
    # Sets scope for clickwheel, handles which item to be highlighted, ready for selection
    def cw_handler(self, items):
        cw_range = len(items)
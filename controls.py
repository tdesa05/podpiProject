from memory import memory

# Interprets controls based on signals from main.py
class Controls():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When the gui calls this file and its functions, its passing in its whole object reference

    # Recieve and interpret input
    def recieve_input(self, event):
        print(event.keysym)
        if event.keysym == 'BackSpace':
            old_path = memory.get_current_path()
            if old_path.endswith('/MusicLibrary'):
                return old_path
            else:
                new_path = old_path.rsplit("/", 1)[0]
                memory.set_current_path(new_path)
                return new_path
    
    # Sets scope for clickwheel, handles which item to be highlighted, ready for selection
    def cw_handler(self, items):
        cw_range = len(items)
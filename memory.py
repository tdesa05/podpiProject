class Memory():
    def __init__(self):
        super().__init__()
        self.selected:str = ""
        self.current_path:str = ""
        self.current_song:str = ""

    # Getter methods
    def get_selected(self):
        return self.selected
    
    def get_current_path(self):
        return self.current_path

    def get_current_song(self):
        return self.current_song
    
    # Setter methods
    def set_selection(self, selected:str):
        self.selected = str(selected)
    
    def set_current_path(self, current_path:str):
        self.current_path = str(current_path)

    def set_current_song(self, current_song:str):
        self.current_song = str(current_song)

memory = Memory()
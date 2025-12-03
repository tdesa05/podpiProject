# Stores shared program memory
class Memory():
    def __init__(self):
        super().__init__()
        self.selected:str = ""
        self.current_path:str = ""
        self.current_song:str = ""
        self.scroll_direction:str = ""
        self.scroll_x:float = 0

    # Getter methods
    def get_selected(self):
        return self.selected
    
    def get_current_path(self):
        return self.current_path

    def get_current_song(self):
        return self.current_song
    
    def get_scroll_direction(self):
        return self.scroll_direction
    
    def get_scroll_x(self):
        return self.scroll_x

    # Setter methods
    def set_selection(self, selected:str):
        self.selected = str(selected)
    
    def set_current_path(self, current_path:str):
        self.current_path = str(current_path)

    def set_current_song(self, current_song:str):
        self.current_song = str(current_song)
    
    def set_scroll_direction(self, scroll_direction:str):
        self.scroll_direction = str(scroll_direction)
    
    def set_scroll_x(self, scroll_x:float):
        self.scroll_x = float(scroll_x)

memory = Memory()
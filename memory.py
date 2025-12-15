import json
import os


DATA_FILE = "data.json"
# Stores shared program memory
# In other classes just call the variable like, memory.selected etc.
class Memory():
    def __init__(self):
        self.selected:list = [] # File that user is currently hovering over
        self.current_path:str = "" # Current path in files (not current path of playing song)

        # Saved variables
        self.current_song:str = "" # Current song playing
        self.previous_song:str = "" # Previous song played
        self.shuffle:bool = False # Whether or not shuffle is active
        self.volume_lvl:int = 0 # Volume level

        self.scroll_direction:str = "" # Direction text is moving in
        self.scroll_x:float = 0 # Position of text (x-axis) 
        
        self.load() # Load saved data on launch

    # Turns memory variables into dictionary
    def to_dict(self):
        return {
            "current_song": self.current_song,
            "previous_song": self.previous_song,
            "shuffle": self.shuffle,
            "volume_lvl": self.volume_lvl
        }
    
    # Save current variables into dictionary for json file
    def save(self):
        try:
            with open(DATA_FILE, 'w') as f:
                # Dumps current data as dict form into json file
                data = json.dump(self.to_dict(), f, indent = 4)
        except Exception as e:
            print(f"Error saving current data: {e}")

    # Load json file, set variables to dictionary
    def load(self):
        if not os.path.exists(DATA_FILE):
            return # If data file not existent, return
        try:
            with open(DATA_FILE,'r') as f: # Open json in read mode, as variable f
                data = json.load(f)
                # Update variables safely (using .get avoids crash if key missing)
                self.current_song = data.get("current_song", "")
                self.previous_song = data.get("previous_song", "")
                self.shuffle = data.get("shuffle", False)
                self.volume_lvl = data.get("volume_lvl", 0)
        except Exception as e:
            print(f"Error loading saved data: {e}")

memory = Memory()
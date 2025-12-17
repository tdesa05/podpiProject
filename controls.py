from memory import memory
import socket
import threading

# Gemini AI heavily helped with implementation of clickwheel components, based on Dupont's driver

# --- Configuration ---
UDP_IP = "127.0.0.1" # Listen to localhost
UDP_PORT = 9090      # Same port as C driver

# Button mapping of click wheel (names used)
BUTTON_MAP = {
    8:  "CENTER",
    12: "MENU",
    11: "PLAY",
    10: "PREV",
    9:  "NEXT",
    29: "TOUCH"
}

# Interprets controls based on signals from main.py
class Controls():
    def __init__(self, gui, playback):
        super().__init__()
        self.gui = gui # When another file calls this file and its functions, its passing in its whole object reference
        self.playback = playback

        # A flag to control pausing. 
        # set() = Running (True)
        # clear() = Paused (False)
        self.is_running = threading.Event()
        self.is_running.set()  # Start as "Running"
        
        # A flag to kill the thread completely when app closes
        self.should_exit = False

    # Recieve and interpret input using keyboard
    def keyboard_input(self, event):
        print(event.keysym)
        if event.keysym == 'BackSpace':
            if self.gui.navbar.get() == 'Files':
                old_path = memory.current_path
                if old_path.endswith('/MusicLibrary'):
                    return
                else:
                    new_path = old_path.rsplit("/", 1)[0]
                    memory.current_path = new_path
                    self.gui.add_to_frame(new_path)
            else:
                pass
        elif event.keysym == 'space':
            self.playback.song_action('pause')
        elif event.keysym == 'q':
            shuffle = memory.shuffle
            if shuffle:
                shuffle = False
            else:
                shuffle = True
            self.playback.check_shuffle()
        elif event.keysym == 'a':
            self.gui.playback.song_action('skip')
        elif event.keysym == 'z':
            self.playback.song_action('shuffle')

    # Pauses clickwheel input
    def pause_input(self):
        print("Clickwheel Paused")
        self.is_running.clear()

    # Resumes clickwheel input
    def resume_input(self):
        print("Clickwheel Resumed")
        self.is_running.set()

    # Shuts down cw_handler function
    def stop_thread(self):
        self.should_exit = True

    # Handles button presses of clickwheel
    def cw_button(self, btn_name, state_str):
        if btn_name == "CENTER":
            pass # Will access the command of selected button (memory selected button)
        elif btn_name == "MENU":
            self.gui.navbar.set("Files")
        elif btn_name == "PLAY":
            self.playback.song_action('play')
        elif btn_name == "PREV":
            self.playback.song_action('back')
        elif btn_name == "NEXT":
            self.playback.song_action('skip')



    # FUNCTION CAN NOT BE MANUALLY CALLED, USE OTHER FUNCTIONS TO STOP/START
    # Interprets data driver hosts on ip and port, triggers appropriate functions
    def cw_handler(self):
        # Create socket and bind to the ip + port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        print(sock)
        # Set timeout once every 100ms so loop doesnt freeze
        sock.settimeout(0.1)
        last_wheel_pos = -1
        while not self.should_exit:
            # Check if paused
            if not self.is_running.is_set():
                # Sleep and skip logic
                self.is_running.wait(timeout=0.1) 
                continue

            try:
                # Buffer size is 3 because the C driver sends exactly 3 bytes
                data, addr = sock.recvfrom(3) 

                # Parse the bytes (Python treats bytes as integers 0-255)
                btn_id = data[0]
                btn_state = data[1]
                wheel_pos = data[2]

                # --- Handle Buttons ---
                # The C driver sends 255 (0xFF) if no button event occurred in this packet
                if btn_id != 255:
                    btn_name = BUTTON_MAP.get(btn_id, f"Unknown ({btn_id})")
                    state_str = "PRESSED" if btn_state == 1 else "RELEASED"
                    print(f"[BUTTON] {btn_name} : {state_str}")
                    self.gui.after(0, self.cw_button, btn_name, state_str) # As it can change GUI


                # --- Handle Wheel ---
                print(f"[WHEEL]  Position: {wheel_pos}")

                # Initialise first wheel pos
                if last_wheel_pos == -1:
                    last_wheel_pos = wheel_pos
                    continue

                diff = wheel_pos - last_wheel_pos

                # Safety to ensure massive movements aren't recorded wrong
                # As the wheel is 0-256, this negates the chances of diff equalling number outside that range.
                if diff > 200: # Moved clockwise a large amount
                    diff -= 256 
                elif diff < -200:
                    diff += 256

                if diff != 0:
                    # Have to use self.gui.after in order to call functions in other gui class, that updates tkinter widgets
                    # This ensures program calls function when safe to do so, tkinter is in charge
                    self.gui.after(0, self.gui.cw_interaction, diff) # Safe call when touching GUI

                last_wheel_pos = wheel_pos
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error: {e}")
                break
        sock.close()
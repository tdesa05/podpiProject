from memory import memory
import socket

# Gemini AI heavily helped with implementation of clickwheel components, based on Dupont's driver

# --- Configuration ---
UDP_IP = "127.0.0.1" # Listen to localhost
UDP_PORT = 9090      # Same port as C driver
last_wheel_pos = -1

# Button mapping of click wheel
BUTTON_MAP = {
    8:  "CENTER",
    12: "MENU (UP)",
    11: "PLAY/PAUSE (DOWN)",
    10: "PREV (LEFT)",
    9:  "NEXT (RIGHT)",
    29: "TOUCH (Surface)"
}

# Interprets controls based on signals from main.py
class Controls():
    def __init__(self, gui, playback):
        super().__init__()
        self.gui = gui # When another file calls this file and its functions, its passing in its whole object reference
        self.playback = playback
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
        elif event.keysym == 'space':
            self.playback.song_action('pause')
        elif event.keysym == 'q':
            shuffle = memory.get_shuffle()
            if shuffle:
                shuffle = False
            else:
                shuffle = True
            self.playback.check_shuffle()
        elif event.keysym == 'a':
            self.gui.playback.song_action('skip')
        elif event.keysym == 'z':
            self.playback.song_action('shuffle')


    # Interprets data driver hosts on ip and port, sends relevant commands to interface
    def cw_handler(self):
        # Create socket and bind to the ip + port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        try:
            while True:
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

                # --- Handle Wheel ---
                # You can add logic here to compare this to the 'last_pos'
                # to determine if it moved Clockwise or Counter-Clockwise
                print(f"[WHEEL]  Position: {wheel_pos}")

        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            sock.close()
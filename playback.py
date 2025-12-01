import vlc

# Initialise VLC
instance = vlc.Instance("--vout=dummy")
player = instance.media_player_new() # type: ignore
print(player)


# Handles playback of music files / streaming
class Playback():
    def __init__(self, gui):
        super().__init__()
        self.gui = gui # When the gui calls this file and its functions, its passing in its whole object reference

    # Handles audio playback based on given parameters
    def recieve_song(self, fp:str, option:str):
        media = instance.media_new(fp) # type: ignore
        player.set_media(media)

        if option == "play":
            player.play()
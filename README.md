This is a portable VLC based media player, using an SPI screen, customtkinter interface and interchangeable DAC.
The GUI looks for music stored in MusicLibrary folder (in same directory as main.py)

Screen Waveshare FBCP driver tutorial https://www.waveshare.com/wiki/2inch_LCD_Module#Working_with_Raspberry_Pi:
- Had to use Raspbian Bullseye (Lite 32 bit) to get screen working
- Using X (no openbox) to show python window


* Currently it assumes the structure MusicLibrary/Artist/Album [Year]/Song
* Used PiCard to fetch metadata for my song library, metadata is assumed by scripts
* File name of song contains numbering such as 01 Changes, 02 Life on Mars. If multiple discs 1-01, 1-02, 2-01, 2-02 ... 


#PLEASE NOTE THIS LIST MAY CHANGE, I'M ONLY IN THE EARLY STAGES, I HAVE NOT BUILT IN ALL FUNCTIONALITY YET
I am using:
- Raspberry Pi Zero 2W (Raspberry Pi OS Lite 32bit)
  
- Waveshare 2inch IPS LCD ST7789V (Amazon)

- 2400mah lithium battery 3.7V (pulled out of old battery bank)
  
- 18650 Type-c charging board (AliExpress)
- Mini 8*2.55mm Button-type Vibration Motor DC 2V-6V 3.7V (AliExpress)
- MT3608 boost module, to push battery to 5V (AliExpress)
- iPod 4th gen clickwheel + 8pin 0.5mm breakout board (AliExpress)
- 2 pin buttons, 3 pin slide switches (AliExpress)
- KY-040 rotary encoder (AliExpress)



// Compile with:
// gcc -Wall -pthread -o click click.c -lpigpio -lrt

#include <pigpio.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 

// --- Configuration ---
#define CLOCK_PIN 23    // GPIO 23 (Physical Pin 16)
#define DATA_PIN 24     // GPIO 24 (Physical Pin 18)
#define BIT_COUNT 32
#define PORT 9090 
#define MAXLINE 1024 

#define CENTER_BUTTON_BIT 7
#define LEFT_BUTTON_BIT 9
#define RIGHT_BUTTON_BIT 8
#define UP_BUTTON_BIT 11
#define DOWN_BUTTON_BIT 10
#define WHEEL_TOUCH_BIT 29

#define BUFFER_SIZE 3
#define BUTTON_INDEX 0
#define BUTTON_STATE_INDEX 1
#define WHEEL_POSITION_INDEX 2

// --- Globals ---
uint32_t bits = 0;
uint32_t lastBits = 0;
uint8_t bitIndex = 0;
uint8_t oneCount = 0;
uint8_t recording = 0;
uint8_t dataBit = 1;

// Button mapping
char buttons[] = { 
    CENTER_BUTTON_BIT, 
    LEFT_BUTTON_BIT, 
    RIGHT_BUTTON_BIT, 
    UP_BUTTON_BIT, 
    DOWN_BUTTON_BIT, 
    WHEEL_TOUCH_BIT
};

const uint32_t PACKET_START = 0b01101;

int sockfd; 
char buffer[BUFFER_SIZE]; 
char prev_buffer[BUFFER_SIZE];
struct sockaddr_in servaddr; 

// --- Helper Functions ---

// FIXED: Removed (k-1) to prevent undefined behavior
uint32_t setBit(uint32_t n, int k) { 
    return (n | (1 << k)); 
} 
  
// FIXED: Removed (k-1)
uint32_t clearBit(uint32_t n, int k) { 
    return (n & (~(1 << k))); 
} 

// --- Core Logic ---

void sendPacket() {
    if ((bits & PACKET_START) != PACKET_START) {
        return;
    }

    // Reset buffer
    memset(buffer, -1, BUFFER_SIZE);
    
    // Check buttons
    for (size_t i = 0; i < sizeof(buttons); i++) {
        char buttonIndex = buttons[i];
        if ((bits >> buttonIndex) & 1 && !((lastBits >> buttonIndex) & 1)) {
            buffer[BUTTON_INDEX] = buttonIndex;
            buffer[BUTTON_STATE_INDEX] = 1;
            printf("Button PRESSED: %d\n", buttonIndex);
        } else if (!((bits >> buttonIndex) & 1) && (lastBits >> buttonIndex) & 1) {
            buffer[BUTTON_INDEX] = buttonIndex;
            buffer[BUTTON_STATE_INDEX] = 0;
            printf("Button RELEASED: %d\n", buttonIndex);
        }
    }

    uint8_t wheelPosition = (bits >> 16) & 0xFF;
    buffer[WHEEL_POSITION_INDEX] = wheelPosition;

    if (memcmp(prev_buffer, buffer, BUFFER_SIZE) == 0) {
        return;
    }

    lastBits = bits;

    sendto(sockfd, (const char *)buffer, BUFFER_SIZE, 
        MSG_CONFIRM, (const struct sockaddr *) &servaddr,  
            sizeof(servaddr)); 
    
    memcpy(prev_buffer, buffer, BUFFER_SIZE);
}

// Ensure this function is defined BEFORE main
void onClockEdge(int gpio, int level, uint32_t tick) {
    // --- DEBUG: SANITY CHECK ---
    // If you see this print, wiring is GOOD. If not, wiring is BAD.
    printf("CLOCK EDGE DETECTED: %d\n", level);

    if (!level) return; // Only process rising edge

    if (dataBit == 0) {
        recording = 1;
        oneCount = 0;
    } else {
        if (++oneCount >= BIT_COUNT) {
            recording = 0;
            bitIndex = 0;
        }
    }

    if (recording == 1) {
        if (dataBit) {
            bits = setBit(bits, bitIndex);
        } else {
            bits = clearBit(bits, bitIndex);
        }

        if (++bitIndex == 32) {
            bitIndex = 0;
            sendPacket();
        }
    }
}

// Ensure this function is defined BEFORE main
void onDataEdge(int gpio, int level, uint32_t tick) {
    dataBit = level;
}

// FIXED: Changed 'void *args' to 'void' (Standard C)
int main(void){
  
    // Socket Setup
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 
  
    memset(&servaddr, 0, sizeof(servaddr)); 
    servaddr.sin_family = AF_INET; 
    servaddr.sin_port = htons(PORT); 
    servaddr.sin_addr.s_addr = INADDR_ANY; 

    // GPIO Setup
    if (gpioInitialise() < 0) {
       fprintf(stderr, "pigpio initialisation failed\n");
       exit(1);
    }

    gpioSetPullUpDown(CLOCK_PIN, PI_PUD_UP);
    gpioSetPullUpDown(DATA_PIN, PI_PUD_UP);

    // Register interrupts
    gpioSetAlertFunc(CLOCK_PIN, onClockEdge);
    gpioSetAlertFunc(DATA_PIN, onDataEdge);

    printf("Driver started on PORT %d. Spin the wheel!\n", PORT);

    while(1) {
        sleep(1); // Save CPU
    };

    gpioTerminate();
    return 0;
}
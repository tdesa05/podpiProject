// gcc -Wall -pthread -o click click.c -lpigpio -lrt
// sudo ./click

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
#define CLOCK_PIN 23 
#define DATA_PIN 24     
#define BIT_COUNT 32
#define PORT 9090 
#define BUFFER_SIZE 3

// --- Globals ---
uint32_t bits = 0;
uint32_t lastBits = 0;
uint8_t bitIndex = 0;
uint8_t oneCount = 0;
uint8_t recording = 0;
uint8_t dataBit = 1;

// Standard Synaptics Header (We will verify this against your output)
const uint32_t PACKET_START = 0b01101; 

int sockfd; 
char buffer[BUFFER_SIZE]; 
struct sockaddr_in servaddr; 

// --- Helper Functions ---

// Prints bits 0 to 31 (Left to Right)
void printBinary(uint32_t value) {
    for(uint8_t i = 0; i < 32; i++) {
        if (value & 1) printf("1");
        else printf("0");
        value >>= 1;
    }
}

uint32_t setBit(uint32_t n, int k) { 
    return (n | (1 << k)); 
} 
  
uint32_t clearBit(uint32_t n, int k) { 
    return (n & (~(1 << k))); 
} 

// --- Core Logic ---

void sendPacket() {
    // --- DEBUG MODE ON --- 
    // This will print EVERY packet the wheel sends so we can decode it.
    printf("Raw: ");
    printBinary(bits);

    if ((bits & PACKET_START) == PACKET_START) {
        printf("  <-- MATCH! (Valid Packet)");
        // If it matches, we decode the position to show it works
        uint8_t wheelPosition = (bits >> 16) & 0xFF;
        printf(" Position: %d", wheelPosition);
    } else {
        printf("  <-- No Match (Header mismatch)");
    }
    printf("\n");

    bits = 0; // Reset for cleanliness
}

void onClockEdge(int gpio, int level, uint32_t tick) {
    if (!level) return; // Only process rising edge

    // If data is LOW, we might be starting a packet
    if (dataBit == 0) {
        recording = 1;
        oneCount = 0;
    } else {
        // If we see 32 "1"s in a row, the line is idle. Reset.
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

void onDataEdge(int gpio, int level, uint32_t tick) {
    dataBit = level;
}

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
    if (gpioInitialise() < 0) exit(1);

    gpioSetPullUpDown(CLOCK_PIN, PI_PUD_UP);
    gpioSetPullUpDown(DATA_PIN, PI_PUD_UP);
    gpioSetAlertFunc(CLOCK_PIN, onClockEdge);
    gpioSetAlertFunc(DATA_PIN, onDataEdge);

    printf("--- DEBUG MODE STARTED ---\n");
    printf("Spin the wheel. You should see 'Raw: 10110...' lines.\n");
    printf("Copy the output and share it!\n\n");

    while(1) {
        sleep(1);
    };

    gpioTerminate();
    return 0;
}
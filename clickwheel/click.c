// gcc -Wall -pthread -o click click.c -lpigpio -lrt
// sudo ./click

#include <pigpio.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> 

#define CLOCK_PIN 23    // GPIO 23 (Physical Pin 16)
#define DATA_PIN 24     // GPIO 24 (Physical Pin 18)

// Global variable to hold the latest data state
volatile int currentDataLevel = 1;

void onDataEdge(int gpio, int level, uint32_t tick) {
    currentDataLevel = level;
}

void onClockEdge(int gpio, int level, uint32_t tick) {
    // Only print on the Rising Edge (when clock goes from 0 to 1)
    if (level == 1) {
        printf("%d", currentDataLevel);
        fflush(stdout); // Force it to print immediately
    }
}

int main(void){
    if (gpioInitialise() < 0) exit(1);

    // Set internal pull-up resistors (Crucial!)
    gpioSetPullUpDown(CLOCK_PIN, PI_PUD_UP);
    gpioSetPullUpDown(DATA_PIN, PI_PUD_UP);

    // Listen for changes
    gpioSetAlertFunc(CLOCK_PIN, onClockEdge);
    gpioSetAlertFunc(DATA_PIN, onDataEdge);

    printf("--- MATRIX MODE: RAW BIT STREAM ---\n");
    printf("Spin the wheel! You should see 1s and 0s appear below.\n");
    printf("-----------------------------------------------------\n");

    while(1) {
        sleep(1);
    };

    gpioTerminate();
    return 0;
}
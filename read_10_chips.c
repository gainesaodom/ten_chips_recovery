/*
Reading Program for the 23A1024 SRAM Chips.

To be used for the reading of ten SRAMs. Use a 70% square wave PWM with 5s period.

Author: Gaines Odom
Advisor: Ujjwal Guin
Institution: Auburn University
Created: 11/1/2024
Revised: 11/4/2024

*/

#include <stdio.h>
#include <errno.h>
#include <stdint.h>
#include <linux/spi/spidev.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <string.h>
#include <inttypes.h>
#include <wiringPi.h>

#include "spi23x1024.c"

#define FGEN_PIN 0
static int select_line_pin [4] = {1,2,3,4,5};  
char date [100];
char file_name [132];
char main_dir [150];
char chip_dir [100];
volatile int s=1;
volatile int chip_num=1;


int create_and_change_directory(const char *dir_name) {
    struct stat st = {0};
	
    // Check if directory exists
    if (stat(dir_name, &st) == -1) {
        // Directory does not exist, so create it
        if (mkdir(dir_name, 0777) == 0) {
			chdir(dir_name);
            return 0;
        } else {
            return 1; // error making directory
        }
    } else {
        return 0;
    }
}

void change_select_pin(int chip_num) 
{
	for (int i = 0; i < sizeof(select_line_pin); i++) 
	{
        int bit = (chip_num >> i) & 1; // Extract the i-th bit of chip_num
        digitalWrite(select_line_pin[i], bit); // Set the pin based on the extracted bit value	
	}
}


void chip_on(void)
{
	if (s % 100==1)
	{
		snprintf(chip_dir, sizeof(chip_dir), "chip_%d", chip_num);
		if(create_and_change_directory("chip_", chip_num)!=0)
				printf("Important error: error with creating new directory. Stop and check for errors.");
	}
	
    if (chip_num <= 10) {
        printf("Starting Read %d for Chip %d... ", s, chip_num);

        snprintf(file_name, sizeof(file_name), "chip%d_%d.csv", chip_num, s);
        FILE *file = fopen(file_name, "w");  

        fprintf(file, "Address,Word\n");

        // SPI_MEM_MAX_ADDRESS
            for (int i = 0; i <= SPI_MEM_MAX_ADDRESS; i++)
            {
                uint8_t f = spi_mem_read_byte(i);
                fprintf(file, "%05" PRIx32 ",%02" PRIx8 "\n", i, f);
            }
        fclose(file);
        printf("Done!\n");
    }
    else 
    {
    printf("Completely Done!\n");
}
s++;
        if (s == 101)
        {
            spi_mem_close();
			chip_num++;
			change_select_pin(chip_num);
			spi_mem_init(5000000);
			s=1;
			chdir(main_dir);
			
        }
}


int main()
{
    printf("What is today's date? (Use format JUL4 for July 4th): ");
    scanf("%99s", date);
    mkdir(date, 0777);
    chdir(date);
	getcwd(main_dir, sizeof(main_dir));
    spi_mem_init(5000000);

    if (wiringPiSetup() == -1) {
        printf("WiringPi initialization failed.\n");
        return 1;
    }

    pinMode(FGEN_PIN, INPUT);
	
	for (int x = 0; x <= sizeof(select_line_pin); x++)
		pinMode(select_line_pin[x], OUTPUT);

    // Set up the interrupt handler
    if (wiringPiISR(FGEN_PIN, INT_EDGE_RISING, &chip_on) < 0) {
        printf("Unable to set up ISR.\n");
        return 1;
    }

    pullUpDnControl(FGEN_PIN, PUD_DOWN);

    while(chip_num <= 10)
    {

    }

    // printf("done\n");
}

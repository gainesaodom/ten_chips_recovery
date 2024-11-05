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
volatile int chip_num=1;


int check_all_cells(void)
{
	uint8_t x = 0;
	
	for (address_idx = 0; address_idx <= SPI_MEM_MAX_ADDRESS; address_idx++) {
		//printf("%x\n", address_idx);
		uint8_t next_value = 0;
		spi_mem_write_byte(address_idx, next_value);
		uint8_t f = spi_mem_read_byte(i);
		if (x || f != 0) 
		{
			printf("Error reading/writing at chip %d. Check its connections.", chip_num);
			return 1;
		}
	}	
	return 0;
}

void change_select_pin(int chip_num) 
{
	for (int i = 0; i < sizeof(select_line_pin); i++) 
	{
        int bit = (chip_num >> i) & 1; // Extract the i-th bit of chip_num
        digitalWrite(select_line_pin[i], bit); // Set the pin based on the extracted bit value	
	}
}

int main()
{    
    spi_mem_init(5000000);

    if (wiringPiSetup() == -1) {
        printf("WiringPi initialization failed.\n");
        return 1;
    }
	
	for (int x = 0; x <= sizeof(select_line_pin); x++)
		pinMode(select_line_pin[x], OUTPUT);

    while(chip_num <= 10)
    {
		check_all_cells();
		chip_num++;		
		change_select_pin(chip_num);
    }

    printf("Done.\n");
}

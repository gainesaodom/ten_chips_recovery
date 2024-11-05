#include <stdint.h>
#include <stdbool.h>
#include "spi23x1024.c"

uint16_t img_write() {

    uint8_t csv_data[131072];
    FILE *file =fopen("Aubie_1024.csv", "r");

    if (file == NULL) {
        perror("Error opening file");
        return 1;
    }

    // Discard the first line (header)
    char buffer[16];
    if (fgets(buffer, sizeof(buffer), file) == NULL) {
        perror("Error reading header");
        fclose(file);
        return 1;
    }

    for (int i = 0; i < 131072; i++) {
        if (fgets(buffer, sizeof(buffer), file) == NULL) {
            perror("Error reading data");
            fclose(file);
            return 1;
        }
        
        // Parse the "Address" and "Byte" data
        unsigned int address;
        unsigned int byte;
        if (sscanf(buffer, "%4x,%2x", &address, &byte) != 2) {
            perror("Error parsing data");
            fclose(file);
            return 1;
        }

        // Store the byte data in the array
        csv_data[i] = (uint8_t)byte;
    }

    fclose(file);

    spi_mem_init(5000000);
	uint16_t address_idx;
	for (address_idx = 0; address_idx <= SPI_MEM_MAX_ADDRESS; address_idx++) {
		//printf("%x\n", address_idx);
		uint8_t next_value = csv_data[address_idx];
		spi_mem_write_byte(address_idx, next_value);
	}	
    spi_mem_close();
    printf("Done Writing Image to Chips.\n");
    return 0;
}

int main()
{
    if (img_write() != 0)  {
        printf("Error: image not written.");
    }
}

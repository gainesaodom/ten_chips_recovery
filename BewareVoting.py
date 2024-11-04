from __future__ import print_function
import csv
import os
from PIL import Image

FIRST_BANDING_LIMITER = 16384
LAST_BANDING_LIMITER = 49150


def create_recovery(votes,width,height): 
    pix_val = []
    for vote in votes:
        if vote == 2: pix_val.append(128)
        if vote == 1: pix_val.append(0)
        if vote == 0: pix_val.append(255)
    img = Image.new('RGB', (width, height), color='white')
    for y in range(height):
        for x in range(width):
            pixel_index = y * width + x
            pixel_value = pix_val[pixel_index]
            img.putpixel((x, y), (pixel_value,pixel_value,pixel_value))
    return img

def maj_fpu_voting(aged_list, new_list):
    votelist = [0] * (len(new_list))
    newlist = []
    
    for i in range(len(aged_list)):
        # Perform subtraction
        diff = aged_list[i] - new_list[i]
        # Update votelist based on the result
        if (diff <= -1):
            votelist[i] -= 1
        elif (diff >= 1):
            votelist[i] += 1

    for item in votelist: 
        # Update votelist based on the result
        if item < 0:
            newlist.append(1)
        elif item > 0:
            newlist.append(0)
        else: newlist.append(2)

    votelist = newlist
    return votelist

# .csv Decoding function. Takes .csv files of the format "Address,Word" and returns int list of addresses and int list of binary values.
def read_csv(filename):
    addresses = []
    bit_list = []
    bits = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader) # skips "Address,Word" header line
        for row in csvreader:
            address, byte = row # row = address: in leftmost space, byte: in rightmost space
            addresses.append(int(address, 16))  # Turns 4 digit hex address into decimal int value list
            bit_list.append(bin(int(byte, 16))[2:].zfill(8))    # Turns 2 digit hex byte into 8 bit binary string list

    # Create a list of 1-bit strings from 8-bit binary strings        
    for byte in bit_list:
        for bit in byte:  
            bits.append(bit)
    
    # Turn 1-bit strings into 1-bit ints
    bits = [int(bit) for bit in bits]

    return addresses, bits

def compare_aging(votes, aging_data):
    perc_recov = 0
    shared_set = [2] * len(aging_data)
    for i in range(len(votes)):
        if (votes[i] == aging_data[i]): 
            perc_recov += 1
            shared_set[i] = votes[i]
    perc_recov = perc_recov/39936

    return perc_recov, shared_set

def main():
    try:
        new_weight, aged_weight, new_bitlists, aged_bitlists, vote_list, aging_data, new_votes = ([] for i in range(7))
        # shared = []

        prevdir = os.getcwd() # Purely for clarity of use

        # Get directory
        input_dir = input("Enter the input directory of the new chip: ")
       
        # If directory doesn't exist, throw error
        if not os.path.exists(input_dir):
            raise FileNotFoundError("This directory does not exist.")
        os.chdir(input_dir)

        one_or_two = input("Chip 1 or Chip 2? ([else]/2): ")
        if (one_or_two == '2') :
            itera = 201
            zp = 101
        else : 
            itera = 101
            zp = 1

        for i in range(zp, itera) :
            if not os.path.exists(input_dir+'_'+str(i)+'.csv'):
                raise FileNotFoundError("File '"+input_dir+"_"+str(i)+".csv' does not exist.")
            
            a, b = read_csv(input_dir+'_'+str(i)+'.csv')
            new_bitlists.append(b)           

        for nums in zip(*new_bitlists):
            total = sum(nums)
            new_weight.append(total)

        os.chdir(prevdir)  

        target_dir = input("Enter the input directory of the target chip: ")
    
        # If directory doesn't exist, throw error
        if not os.path.exists(target_dir):
            raise FileNotFoundError("This directory does not exist.")
        os.chdir(target_dir)

        for i in range(zp, itera) :
            if not os.path.exists(target_dir+'_'+str(i)+'.csv'):
                raise FileNotFoundError("File '"+target_dir+"_"+str(i)+".csv' does not exist.")
        
            a, b = read_csv(target_dir+'_'+str(i)+'.csv')
            aged_bitlists.append(b)

        os.chdir(prevdir)

        for nums in zip(*aged_bitlists):
            total = sum(nums)
            aged_weight.append(total)

        vote_list.append(maj_fpu_voting(aged_weight, new_weight))

        while (input("Add a pair of aged and new power-up states? [y/n] ") != 'n') :

            new_bitlists.clear()
            new_weight.clear()
            aged_bitlists.clear()
            aged_weight.clear()

            input_dir = input("Enter the input directory of the new chip: ")

            # If directory doesn't exist, throw error
            if not os.path.exists(input_dir):
                raise FileNotFoundError("This directory does not exist.")
            os.chdir(input_dir)
        
            one_or_two = input("Chip 1 or Chip 2? ([else]/2): ")
            if (one_or_two == '2') :
                itera = 201
                zp = 101
            else : 
                itera = 101
                zp = 1

            for i in range(zp, itera) :
                if not os.path.exists(input_dir+'_'+str(i)+'.csv'):
                    raise FileNotFoundError("File '"+input_dir+"_"+str(i)+".csv' does not exist.")
                
                a, b = read_csv(input_dir+'_'+str(i)+'.csv')
                new_bitlists.append(b)

            for nums in zip(*new_bitlists):
                total = sum(nums)
                new_weight.append(total)

            os.chdir(prevdir)

            target_dir = input("Enter the input directory of the target chip: ")
        
            # If directory doesn't exist, throw error
            if not os.path.exists(target_dir):
                raise FileNotFoundError("This directory does not exist.")
            os.chdir(target_dir)

            for i in range(zp, itera) :
                if not os.path.exists(target_dir+'_'+str(i)+'.csv'):
                    raise FileNotFoundError("File '"+target_dir+"_"+str(i)+".csv' does not exist.")
            
                a, b = read_csv(target_dir+'_'+str(i)+'.csv')
                aged_bitlists.append(b)

            os.chdir(prevdir)

            for nums in zip(*aged_bitlists):
                total = sum(nums)
                aged_weight.append(total)

            vote_list.append(maj_fpu_voting(aged_weight,new_weight))

        for votes in zip(*vote_list):
            if(votes.count(0) > votes.count(1)): new_votes.append(0)
            elif(votes.count(1) > votes.count(0)): new_votes.append(1)
            else: new_votes.append(2)


        # Create bitmap directory (if necessary)
        if not os.path.exists('RECOVER_BMPs'):
            os.mkdir('RECOVER_BMPs')

        adr, aging_data = read_csv('WrittenImage.csv')
        recovery, shared = compare_aging(new_votes, aging_data)

        # Create bitmap of recovered data
        recovered_bmp = create_recovery(new_votes, 256, 256)
        recovered_bmp.show()

        # Overlay Recovered data with actual aging data
        # shared_bmp = create_recovery(shared,256,256)
        # shared_bmp.show()

        os.chdir('RECOVER_BMPs')
        save_as = input('Save bitmap png as? (Hint: type "dog" for "dog.png") ')
        # shared_bmp.save(target_dir + 'shared.png')
        recovered_bmp.save(save_as + 'recovered.png')
               
        os.chdir(prevdir)

        print("Data recovered, presented as a decimal: "+ str(recovery))
            # Error Handler
    except Exception as e:
        print(e)

    # Return to program directory, create training data directory and save training data to it
    finally:
        os.chdir(prevdir)    

if __name__ == "__main__":
    main()
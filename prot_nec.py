# FIND THE CODES SENT FROM A REMOTE CONTROL
# USING NEC CODING FOR INFRARED 

from pyb import Pin
import machine
import os
import sys


# detects the times when the 38khz signal
# stay in the high or low state 
def decode_ir():
    # RECEIVE 50 VALUE PAIRS [1/0]
    nletture = 50
    lettura_tot = []
    ingresso = Pin("X10" , Pin.IN, Pin.PULL_UP)
    serie = open("burst.txt","w")
    # SAVE THE SEQUENCE SENT BY THE REMOTE CONTROL IN A LIST
    for i in range(nletture):
        lettura_tot.append(machine.time_pulse_us(ingresso,0))
        lettura_tot.append(machine.time_pulse_us(ingresso,1))
    # SAVE THE LIST TO A TEXT FILE IN THE SD CARD
    for i in range(len(lettura_tot)):
        serie.write(str(lettura_tot[i])+"\n")    
    serie.close()
    extract_bit()
    

# MAIN FUNCTION
# TAKES CARE OF TRANSFORMING THE SEQUENCES OF
# TIMES DETECTED BY decode_ir ()
# IN BIT SEQUENCES 
def extract_bit():
    bitf = "bitfile.txt"
    nomef="burst.txt"
    ottobit = - 1
    count = 0
    flag = False
    f1 = open(nomef, 'r')
    bf = open(bitf,'w')
    
    # I find the position (x), where the sequence of the IR code begins
    # The result is in 'COUNT' 
    while not flag:  
        legge = f1.readline().rstrip('\n')
        count += 1
        try:
            if 9000 < int(legge) < 10000:
                flag = True  # STARTING POINT OF PROTOCOL FOUND (X)
        except ValueError:
            f1.close()
            print("Unknown protocol")
            print("Further updates coming soon")
            sys.exit()
    f1.close()
    
    # MOVE THE FILE PLACE MARK
    # FORWARD OF (count-1) POSITIONS 
    f1 = open(nomef, 'r')
    for i in range(count - 1):
        legge = f1.readline().rstrip('\n')        
    count = 0
    
    # From here I read 66 bits (64 + 2 START BIT) and go out
    while count < 67:
        b1 = f1.readline().rstrip('\n')
        b2 = f1.readline().rstrip('\n')
        count += 2
        # If the readings are not numbers,exits
        if not b1.isdigit() or not b2.isdigit():
            break
        b1 = int(b1)
        b2 = int(b2)
        ottobit = ottobit + 1
        if (b1 > 9000) and (4000 < b2 < 5000):
            print("NEC coding")
            print("START BIT")
        if (b1 < 650) and (b2 < 650):
            print('0', end='')
            bf.write('0')
            if ottobit >= 8:
                print()
                bf.write('\n')
                ottobit = 0
        if (b1 < 650) and (650 < b2 < 1700):
            print('1', end='')
            bf.write('1')
            if ottobit >= 8:
                print()
                bf.write('\n')
                ottobit = 0
        if count > 66:
            if b1 < 650:
                print("BURST CLOSED\n")
    f1.close()
    bf.close()
    flip_bit()
    os.remove("burst.txt")
    

# inverte le stringhe di bit
# e le riporta su file
def flip_bit():
    count = 0
    bitf = "bitfile.txt"
    flipf = "flip.txt"
    bf = open(bitf, 'r')
    ff = open(flipf, 'w')
    while count <= 3:
        read = bf.readline().rstrip('\n')
        count += 1
        # The right bit is MSB so the bits must be read in reverse
        read = list(read)
        read.reverse()
        read = "".join(read)
        ff.write(read + '\n')
    bf.close()
    ff.close()
    conv_bin_dec()
    os.remove("bitfile.txt")


# generate a file with the sequences
# of bits generated by the remote control 
def conv_bin_dec():
    print("Conversion result : ")
    with open("flip.txt",'r') as fr:
        with open("conv.txt",'w') as fw:
            while True:
                line = fr.readline()
                if not line:
                    break
                val = bin2dec(line.strip())
                print(line.strip()," ", val )
                fw.write("{} {}\n".format(line.strip(),val))
    os.remove("flip.txt")


# Convert binary number to decimal
def bin2dec(binario):
    lung = len(binario)
    dec = 0
    for i in range(lung):
        indice = lung - i - 1
        cifra = int(binario[indice]) * pow(2, i)
        dec = dec + cifra
    return dec



decode_ir()





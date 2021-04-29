# TROVA I CODICI INVIATI DA UN TELECOMANDO
# CHE UTILIZZA LA CODIFICA NEC PER L'INFRAROSSO

from pyb import Pin
import machine
import os
import sys


# rileva i tempi in cui il segnale a 38khz
# resta nello stato alto o basso
def decode_ir():
    # RICEVO 50 COPPIE DI VALORI 1/0
    nletture = 50
    lettura_tot = []
    ingresso = Pin("X10" , Pin.IN, Pin.PULL_UP)
    serie = open("burst.txt","w")
    # SALVO LA SEQUENZA INVIATA DAL TELECOMANDO IN UNA LISTA
    for i in range(nletture):
        lettura_tot.append(machine.time_pulse_us(ingresso,0))
        lettura_tot.append(machine.time_pulse_us(ingresso,1))
    # SALVO LA LISTA SU UN FILE DI TESTO NELLA SCHEDA SD 
    for i in range(len(lettura_tot)):
        serie.write(str(lettura_tot[i])+"\n")    
    serie.close()
    extract_bit()
    

# FUNZIONE PRINCIPALE
# SI OCCUPA DI TRASFORMARE LE SEQUENZE DI
# TEMPI RILEVATI DA decode_ir()
# IN SEQUENZE DI BIT
def extract_bit():
    bitf = "bitfile.txt"
    nomef="burst.txt"
    ottobit = - 1
    count = 0
    flag = False
    f1 = open(nomef, 'r')
    bf = open(bitf,'w')
    
    # trovo la posizione (x), dove inizia la sequenza del codice IR
    # Il risultato è in 'COUNT'
    while not flag:  
        legge = f1.readline().rstrip('\n')
        count += 1
        try:
            if 9000 < int(legge) < 10000:
                flag = True  # PUNTO DI INIZIO TROVATO (X)
        except ValueError:
            f1.close()
            print("Protocollo sconosciuto")
            print("Seguiranno aggiornamenti")
            sys.exit()
    f1.close()
    
    # SPOSTO IL SEGNAPOSTO DEL FILE
    # IN AVANTI DI X (count-1) POSIZIONI
    f1 = open(nomef, 'r')
    for i in range(count - 1):
        legge = f1.readline().rstrip('\n')        
    count = 0
    
    # Da qui leggo 66 bit (64+2 START BIT) ed esco
    while count < 67:
        b1 = f1.readline().rstrip('\n')
        b2 = f1.readline().rstrip('\n')
        count += 2
        """Se le letture non sono numeri , esce"""
        if not b1.isdigit() or not b2.isdigit():
            break
        b1 = int(b1)
        b2 = int(b2)
        ottobit = ottobit + 1
        if (b1 > 9000) and (4000 < b2 < 5000):
            print("Codifica NEC")
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
                print("BURST CHIUSURA\n")
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
        # Il bit di destra è MSB quindi i bit vanno letti al contrario
        read = list(read)
        read.reverse()
        read = "".join(read)
        ff.write(read + '\n')
    bf.close()
    ff.close()
    conv_bin_dec()
    os.remove("bitfile.txt")


# genera un file con le sequenze
# di bit generate dal telecomandO
def conv_bin_dec():
    print("Risultato conversione : ")
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


# Converte un numero binario in decimale
def bin2dec(binario):
    lung = len(binario)
    dec = 0
    for i in range(lung):
        indice = lung - i - 1
        cifra = int(binario[indice]) * pow(2, i)
        dec = dec + cifra
    return dec



decode_ir()





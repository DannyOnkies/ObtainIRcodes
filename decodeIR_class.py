"""
    Classe IR REMOTE
"""
from pyb import Pin
import machine
import sys


class IrRemote:
    
    # rileva i tempi in cui il segnale a 38khz
    # resta nello stato alto o basso
    def decode_ir(self):
        # COPPIE DI VALORI TEMPORALI
        # VALORE SPERIMENTALE
        nletture = 38
        lettura_tot = []
        ingresso = Pin("X5" , Pin.IN, Pin.PULL_UP)
        # SALVO LA SEQUENZA INVIATA DAL TELECOMANDO IN UNA LISTA
        for i in range(nletture):
            lettura_tot.append(machine.time_pulse_us(ingresso,0))
            lettura_tot.append(machine.time_pulse_us(ingresso,1))
        return lettura_tot
    
    
    def identify_prot(self,lista):
        tmp1 = (self.trovaflag(lista, 8000, 10000, 4300, 4700))
        tmp2 = (self.trovaflag(lista, 4000, 5000, 4000, 5000))
        tmp3 = (self.trovaflag(lista, 2200, 2600, 500, 600))
        # LA FUNZIONE trovaflag RESTITUISCE None
        # QUANDO NON TROVA CORRISPONDENZE
        if tmp1 is not None:
            if tmp1 > 0:
                self.prot_nec(lista)
        elif tmp2 is not None:
            if tmp2 > 0:
                self.prot_samsung(lista)
        elif tmp3 is not None:
            if tmp3 > 0:
                self.prot_sony(lista)


    def trovaflag(self,lista,start,end,start1,end1):
        for count in range(len(lista)-1):
            b1 = lista[count]
            b2 = lista[count+1]
            if (start < b1 < end) and (start1 < b2 < end1) :
                return count+1


    def bin2dec(self,binario):
        lung = len(binario)
        dec = 0
        for i in range(lung):
            indice = lung - i - 1
            cifra = int(binario[indice]) * pow(2, i)
            dec = dec + cifra
        return dec


    def prot_nec(self,lista):
        contabit = 0
        allbit = []
        endbit = False

        first = self.trovaflag(lista, 8000, 10000, 4370, 4700) - 1  # primo elemento del pacchetto
        last = first + 68
        lista = lista[first:last]

        # versione protocollo in bit
        bitcode = int(((last - first) - 3) / 2)
        for count in range(0, len(lista), 2):
            b1 = lista[count]
            b2 = lista[count + 1]
            if (8000 < b1 < 10000) and (4000 < b2 < 5000):  # START BIT
                print("Codifica NEC", bitcode, "bit")
                print("START BIT OK")
            elif (b1 < 700) and (b2 < 700):  # BIT 0
                allbit.append('0')
                contabit += 1
            elif (b1 < 700) and (1500 < b2 < 1700):  # BIT 1
                allbit.append('1')
                contabit += 1
            elif (b1 < 700) and (30000 < b2):  # END BIT
                endbit = True

        a = allbit[0:8]  # 8 bit
        b = allbit[8:16]
        c = allbit[16:24]
        d = allbit[24:32]

        a.reverse()
        b.reverse()
        c.reverse()
        d.reverse()

        a1 = "".join(a)
        b1 = "".join(b)
        c1 = "".join(c)
        d1 = "".join(d)

        print("  Device   ", a1, self.bin2dec(a1))
        print(" |Device|  ", b1, self.bin2dec(b1))
        print("  Comando  ", c1, self.bin2dec(c1))
        print(" |Comando| ", d1, self.bin2dec(d1))
        if endbit:
            print("END BIT")

    def prot_sony(self,lista):
        contabit = 0
        allbit = []

        first = self.trovaflag(lista, 2200, 2600, 500, 600) - 1  # primo elemento del pacchetto
        last = self.trovaflag(lista, 10000, 30000, 2200, 2600)   # ultimo elemento del pacchetto
        lista = lista[first:last]

        # versione protocollo in bit
        bitcode = int(((last - first) - 2) / 2)

        for count in range(0,len(lista),2):
            b1 = lista[count]
            b2 = lista[count+1]
            if (2000 < b1 < 3000) and (500 < b2 < 700):
                print("Codifica SONY",bitcode,"bit" )
                print("START BIT OK")
            elif (1100 < b1 < 1300) and (500 < b2 < 700):
                allbit.append('1')
                contabit += 1
            elif (1100 < b1 < 1300) and (b2 > 10000):
                allbit.append('1')
                contabit += 1
            elif (500 < b1 < 700) and (b2 > 10000):
                allbit.append('0')
                contabit += 1
            elif (500 < b1 < 700) and (500 < b2 < 700):
                allbit.append('0')
                contabit += 1

        # segmento valido per tutte le versioni
        a = allbit[0:7]     # 7 bit
        b = allbit[7:12]    # 5 bit
        a.reverse()
        b.reverse()
        a1 = "".join(a)
        b1 = "".join(b)
        print("Comando  ", a1, self.bin2dec(a1))
        print("Device   ", b1, self.bin2dec(b1))

        # segmento valido per la versione a 20bit
        if bitcode == 20:
            c = allbit[12:20]   # 8 bit
            c.reverse()
            c1 = "".join(c)
            print("Extended ", c1, self.bin2dec(c1))

    def prot_samsung(self,lista):
        contabit = 0
        allbit = []
        endbit = False

        lowbit1 = 450
        lowbit2 = 700
        highbit1 = 1500
        highbit2 = 1700

        first = self.trovaflag(lista, 4000, 5000, 4000, 5000) - 1    # primo elemento del pacchetto
        last = self.trovaflag(lista, 40000, 50000, 4000, 5000)       # ultimo elemento del pacchetto
        lista = lista[first:last]

        # se non trovo l'ultimo elemento del pacchetto , esco
        if last is not None:
            bitcode = int(((last - first) - 3) / 2)
        else:
            sys.exit("Non trovo il bit di chiusura")
        for count in range(0,len(lista),2):
            b1 = lista[count]
            b2 = lista[count+1]
            if (4000 < b1 < 5000) and (4000 < b2 < 5000):#  START BIT
                print("Codifica SAMSUNG",bitcode,"bit" )
                print("START BIT OK")
            elif (lowbit1 < b1 < lowbit2) and (lowbit1 < b2 < lowbit2):#  BIT 0
                allbit.append('0')
                contabit += 1
            elif (lowbit1 < b1 < lowbit2) and (highbit1 < b2 < highbit2):#  BIT 1
                allbit.append('1')
                contabit += 1
            elif (lowbit1 < b1 < lowbit2) and (40000 < b2 < 50000):#  END BIT
                endbit = True

        a = allbit[0:8]
        b = allbit[8:16]
        c = allbit[16:24]
        d = allbit[24:32]

        # rovescio ogni lista
        a.reverse()
        b.reverse()
        c.reverse()
        d.reverse()

        # converto ogni lista in una stringa
        a1 = "".join(a)
        b1 = "".join(b)
        c1 = "".join(c)
        d1 = "".join(d)

        print(" Device  ", a1, self.bin2dec(a1))
        print(" Device  ", b1, self.bin2dec(b1))
        print(" Comando ", c1, self.bin2dec(c1))
        print("|Comando|", d1, self.bin2dec(d1))
        if endbit:
            print("END BIT")


# creo un oggetto irremote
irremote = IrRemote()
# prelevo la lista generata dal telecomando
rawcode = irremote.decode_ir()
# passo la lista alla funzione di decodifica
irremote.identify_prot(rawcode)

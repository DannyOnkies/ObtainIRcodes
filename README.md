# Find out the code sent by an ir remote control
Obtain ir remote control codes using a Pyboard card and a VS1838 receiver
_________________________________________________________________________

**`Purpose of the code`**

When we press the button on the remote how does the TV know what to do?
The answer is in the modulation of the infrared signal coming out of the remote control.
Usually it is a 38 khz PWM signal with a specific coding for each device.
Transmitter and receiver are tuned to the same frequency and use the same coding.
![image]()
In this application I use an ELEGOO remote control supplied with the ARDUINO STARTER KIT.

**`Technical notes`**

In PWM modulation, the duration of the single bit is variable and depends on the logical state of the bit itself.
Usually the longest bit is associated with bit 1 while the shortest bit is associated with bit 0.
Many companies use their own protocol. One of the most used is called NEC and is the one used by my remote control.
It is based on a carrier between 38 and 40 khz. 
Bit 1 is formed by 550μs of light followed by 1650μs of dark, while bit 0 is formed by a high state of 550μs and a low state of equal duration.
A packet sent from the remote contains 32 bits plus a start bit. The start bit is formed by a low pulse of 9mS followed by a low pulse of 4.5mS.
The remaining fields have a length of 8 bits and are transmitted starting with the least significant bit (LSB). 
The denied codes (complement) serve as a prevention against errors and also to make the message duration constant.

**`Software analysis`**

The software consists of 4 (+1) functions.

* decode_ir () The first to be called, which detects the times when the 38 khz pulse train is in the high or low state. It uses the **`machine.time_pulse_us()`** function which returns the time a pulse has been in a specific state.
* extract_bit () checks for the presence of the START BIT. This confirms that the incoming pulses modulated with the NEC protocol. The times recorded by decode_ir () are converted into comprehensible and organized sequences of 1's and 0's
* flip_bit () the data sent by the remote control is in the reverse position and must be reversed.
* conv_bin_dec () using bin2dec () function converts sequences of bits to decimal numbers

The Micropython function is used to calculate the times when pin X10 is high or low
machine.time_pulse_us (pin, pulse_level, timeout_us = 1000000).
The signal sent on pin X10 is compared with "pulse_level". If the signal is different, the function waits for the level to change
if, on the other hand, the level is the same then the timer is started immediately.
The function returns -2 in case of timeout due to waiting for the condition or -1 for timeout due to measurement (no signal).
The recorded times are not exactly the same as the theoretical ones and therefore I had to proceed as follows.
After identifying the START BIT I read pairs of time values (expressed in uS) in order to assign a value of 1 or 0 to each of these pairs.
Remember that the NEC protocol requires:
for the value 1 a signal composed of a time of 550us and then one of 1650us
for the value 0 a signal consisting of a time of 550μs and then a time of 550μs.

**`Final notes`**

The values read, however, are not exactly these, and it is precisely the task of the extract_bit () function to interpret the measured times and return the coherent bit sequences.
I inserted a microSD card into the Pyboard card slot where the **`conv.txt file`** containing the code of the key pressed is saved.
An example of file relating to the ON / OFF key:

> CONV.TXT
> 
> 00000000 0
> 
> 11111111 255
> 
> 01000101 69
> 
> 10111010 186
> 


Soon I try to rewrite the software using classes and objects.
Greetings





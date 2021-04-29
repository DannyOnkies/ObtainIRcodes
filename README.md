# ObtainIRcodes
Obtain ir remote control codes using a Pyboard card and a VS1838 receiver

**`Purpose of the code`**

When we press the button on the remote how does the TV know what to do?
The answer is in the modulation of the infrared signal coming out of the remote control.
Usually it is a 38 khz PWM signal with a specific coding for each device.
Transmitter and receiver are tuned to the same frequency and use the same coding.
In this application I use an ELEGOO remote control supplied with the ARDUINO STARTER KIT.

**`Technical notes`**

In PWM modulation, the duration of the single bit is variable and depends on the logical state of the bit itself.
Usually the longest bit is associated with bit 1 while the shortest bit is associated with bit 0.
Many companies use their own protocol. One of the most used is called NEC and is the one used by my remote control.
It is based on a carrier between 38 and 40 khz. 
Bit 1 is formed by 550uS of light followed by 1650uS of dark, while bit 0 is formed by a high state of 550uS and a low state of equal duration.
A packet sent from the remote contains 32 bits plus a start bit.
The start bit is formed by a low pulse of 9mS followed by a low pulse of 4.5mS.
The remaining fields have a length of 8 bits and are transmitted starting with the least significant bit (LSB). The denied codes (complement) serve as a prevention against errors and also to make the message duration constant.



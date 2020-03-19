# Adjust the pulseio 'board.PIN' if using something else
import pulseio
import board
import adafruit_irremote
import time
from adafruit_circuitplayground.express import cpx

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

def getDutyCycle(saved_pulses):
    duty_cycle_average = 0
    for i in range(0,len(saved_pulses) - 1):
        #print(saved_pulses[i])
        duty_cycle_average += (saved_pulses[i] + saved_pulses[i+1])/2
    duty_cycle_average = duty_cycle_average / 55
    #print("duty cycle average = " + str(duty_cycle_average))
    return duty_cycle_average

def getWandIDFromPulses(saved_pulses):
    # Returns WandID as a string

    duty_cycle = getDutyCycle(saved_pulses)
    duty_cycle_cutoff = duty_cycle / 3
    #binary_array = []
    binary_string = ""

    # saved_pulses is of length 111 (index is 0 .. 110) with each pair being a signal and non-signal.
    #  - special case is the last item (index 110) which is a signal but without the non-signal portion.
    # Will create an array of length 56 with each element being 0 or 1
    # element n will be 0 if saved_pulses[i] is < 1/3 of duty_cycle
    # element n will be 1 if saved_pulses[i] is > 1/3 of duty_cycle
    # then will loop to i+2

    for i in range(0,len(saved_pulses),2):
        if saved_pulses[i] < duty_cycle_cutoff:
            #binary_array.append(0)
            binary_string += "0"
        else:
            #binary_array.append(1)
            binary_string += "1"

    #print(binary_string)
    #print("hexadecimal version")
    binary_in_int = int(binary_string,2)
    hex_value = hex(binary_in_int)
    #print(hex_value)
    #print(hex_value[2:-5])
    return(str(hex_value[2:-5]))



    '''
    Example hex from pink wand:
    0x54eba6020118
    0x54eba6030216
    0x54eba6020316
    So ID is 54eba60

    Example hex from blue wand:
    0x54d4b5020120
    0x54d4b502031e
    0x54d4b503031d
    So ID is 54d4b50

    Need to see if every wand starts with 54 or ends with 0
    '''


pulsein = pulseio.PulseIn(board.REMOTEIN, maxlen=120, idle_state=True)
decoder = adafruit_irremote.GenericDecode()

print("Start of wand detector")

while True:
    pulses = decoder.read_pulses(pulsein)
    if len(pulses) == 111:
        #print("Heard", len(pulses), "Pulses:", pulses)
        wand_id = getWandIDFromPulses(pulses)
        print(wand_id)
        if wand_id == '54d4b50':
            cpx.pixels.fill((130, 0, 100))
            cpx.play_tone(262, 1)
        elif wand_id == '54eba60':
            cpx.pixels.fill((100,100,100))
            cpx.play_tone(294, 1)
        time.sleep(1) #Sleep for 1 second
    '''
    try:
        code = decoder.decode_bits(pulses)
        print("Decoded:", code)
    except adafruit_irremote.IRNECRepeatException:  # unusual short code!
        print("NEC repeat!")
    except adafruit_irremote.IRDecodeException as e:     # failed to decode
        print("Failed to decode: ", e.args)
    '''
    #print("----------------------------")

'''
The wand transmits 56 bits of information. Each bit has a duty cycle of about 1150 microseconds, where the duty cycle is the total time of
each space and pulse pair.

A pulse that takes up under 1/3 of the duty cycle is translated to 0, and a pulse that takes more than 1/3 of the duty cycle is 1.

As the wand's battery level goes down, the duty cycle seems to increase, so my first attempt that was based on static cutoffs stopped
working after a while.

In the resulting 7 bytes, I observed this format with two wands: 00 ID ID ID MO MO MO

The first byte was always 0
The next 3 bytes are the ID of the wand
The last 3 bytes change and might be related to the motion of the wand (or mean something else entirely)
'''

'''
read_pulses(input_pulses, *, max_pulse=10000, blocking=True, pulse_window=0.1, blocking_delay=0.1)[source]
Read out a burst of pulses until pulses stop for a specified period (pulse_window), pruning pulses after a pulse longer than max_pulse.

Parameters:	
input_pulses (PulseIn) – Object to read pulses from
max_pulse (int) – Pulse duration to end a burst
blocking (bool) – If True, will block until pulses found. If False, will return None if no pulses. Defaults to True for backwards compatibility
pulse_window (float) – pulses are collected for this period of time
blocking_delay (float) – delay between pulse checks when blocking
'''

'''
Example 111 pulse from wand:
[281, 815, 309, 812, 280, 816, 276, 846, 278, 817, 286, 811, 282, 838, 285, 810, 286,
810, 591, 582, 282, 814, 569, 605, 280, 815, 569, 579, 305, 818, 286, 809, 564, 609,
566, 582, 573, 574, 279, 843, 572, 576, 277, 818, 597, 578, 567, 580, 597, 577, 285,
811, 573, 575, 309, 812, 281, 815, 569, 605, 570, 578, 275, 820, 304, 818, 286, 811,
282, 812, 311, 812, 280, 814, 310, 813, 571, 575, 570, 604, 280, 820, 272, 820, 282,
839, 285, 811, 282, 812, 312, 811, 593, 555, 278, 842, 281, 815, 277, 819, 285, 836,
569, 580, 283, 838, 568, 580, 564, 584, 279]
'''
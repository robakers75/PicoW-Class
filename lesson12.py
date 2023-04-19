from machine import Pin,PWM
from time import sleep
import array as ary

#####################################################################
#                  RGB Assignment
#
#  Script: The process will ask the user for the color, and through the
#          magic of the Pi, the RGB LED, and 3.3 volts of electricity
#          the color will be presented to the user based on their selection
#
#          1 - Red)
#          2 - Green       
#          3 - Blue
#          4 - Cyan
#          5 - Magenta
#          6 - Yellow
#          7 - Orange
#          8 - white
#
#  Date: 04/11/2023
#
#  Enjoy, copy if you like - Cannot get more open source than this 
#####################################################################


#setup the working storage areas
#setup the pins

redPin=13
greenPin=14
bluePin=15

# also micropython does not have the ability for multidemonal array
# so we have to creat 3 independant lists for Red, green, and Blue.
# this will require the position to be specific to the color selected 
# There must be a better way, but this was the approach I settled with

#LED will use PWM to turn the light on set the duty cycle, and Frequency
redLED=PWM(Pin(redPin))
greenLED=PWM(Pin(greenPin))
blueLED=PWM(Pin(bluePin))

#red
redLED.freq(1000)
redLED.duty_u16(0)
#Green
greenLED.freq(1000)
greenLED.duty_u16(0)
#blue
blueLED.freq(1000)
blueLED.duty_u16(0)

colors=[(255,0,0),     #Red
        (0,255,0),     #Green 
        (0,0,255),     #blue
        (0,255,255),   #Cyan
        (255,0,255),   #Magenta
        (255,255,0),   #Yellow
        (240,10,0),    #Orange
        (255,255,255)] #white

# Magic numbers are frown upon, so storing these in a varable.

#
#  Create common function to turn everything off
#
def reset_duty_cycles():
    redLED.duty_u16(0)
    greenLED.duty_u16(0)
    blueLED.duty_u16(0)
    return

# borrowed this code from Passkkal from lesson 12 (which it was borrowed from adafruit).  Read the AdaFruit
# aritical# to understand the the need to as humans do not see light lineral fashion. 
# gamma correction value used to compensate for non-linearility of human vision
# Based on https://cdn-learn.adafruit.com/downloads/pdf/led-tricks-gamma-correction.pdf
def convert_rgb_to_analog(rgb):
    maxBrightness=65550
    maxRGBValue=255
    gamma=2.8
    rgb = tuple(x / maxRGBValue for x in rgb) # normalize rgb values so they are between 0 and 1
    rgb = tuple(x ** gamma for x in rgb) # apply gamma correction
    rgb = tuple(int(round(x * maxBrightness)) for x in rgb) # convert to 16-bit analog value
    return rgb

# did this just to prove I understood how they tuple works, but since the values never change
# thought I would only calculate the values one time instead of calling it each time.
# the nano second saved would not matter for this program, but may sometime time the future

try:
    analog_list=[]
    for colorValue in colors:
        brightnessValue = convert_rgb_to_analog(colorValue)
        analog_list.append(tuple(brightnessValue))
#    for led_pin, analog_value in zip(colors[0]):

    while True:
    #Begin while Loop ask the user, and make sure they do not mess
    #since we dont want to recalculate each time, lets loop through
    #and store the final
        
        print(f"1 - Red\n2 - Green\n3 - Blue\n4 - Cyan\n5 - Magenta\n6 - Yellow\n7 - Orange\n8 - white\n")
        
#Remember a user can enter anything, we need to make sure the
#the program does not abend
        
        try:      
            myInput=int(input('select a color: '))
        except KeyError:
            reset_duty_cycles()
            continue
#cannot avoid the chec for the right range select form the user
        
        if (myInput >0 and myInput <9):
    
            (redBright,greenBright,blueBright) = analog_list[myInput-1]
              
            redLED.duty_u16(redBright)
            greenLED.duty_u16(greenBright)
            blueLED.duty_u16(blueBright)
            sleep(.5)
        else:
            reset_duty_cycles()
            
except KeyboardInterrupt:
    reset_duty_cycles()
    print("Going Down - Turn everything off")

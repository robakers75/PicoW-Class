from machine import Pin,PWM,ADC
from time import sleep

#####################################################################
#                  RGB Assignment with Controls
#
#  Script: The process will read from a potentiometer and set the red,
#          green, blue values based on how the user turns the dial
#
#  Date: 04/19/2023
#
#  Enjoy, copy if you like - Cannot get more open source than this 
#####################################################################


#setup the working storage areas
#setup the output pins
redPin=13
greenPin=14
bluePin=15
#setup the input pins
redADCPin=28
greenADCPin=27
blueADCPin=26

#LED will use PWM to turn the light on set the duty cycle, and Frequency
redLED=PWM(Pin(redPin))
greenLED=PWM(Pin(greenPin))
blueLED=PWM(Pin(bluePin))

myRed=machine.ADC(redADCPin)
myGreen=machine.ADC(greenADCPin)
myBlue=machine.ADC(blueADCPin)

#red
redLED.freq(1000)
redLED.duty_u16(0)
#Green
greenLED.freq(1000)
greenLED.duty_u16(0)
#blue
blueLED.freq(1000)
blueLED.duty_u16(0)

#
#  Create common function to turn everything off
#
def reset_duty_cycles():
    redLED.duty_u16(0)
    greenLED.duty_u16(0)
    blueLED.duty_u16(0)
    return

# borrowed this code from Passkkal from lesson 12 (which it was borrowed from adafruit). Please Read the AdaFruit
# artical to understand the the need for this as humans do not see light in a lineral fashion. 
# Based on https://cdn-learn.adafruit.com/downloads/pdf/led-tricks-gamma-correction.pdf
def convert_rgb_to_analog(rgb):
    maxBrightness=65550
    maxRGBValue=255
    gamma=2.8
    rgb = rgb / maxRGBValue               # normalize rgb values so they are between 0 and 1
    rgb = rgb ** gamma                    # apply gamma correction
    rgb = int(round(rgb * maxBrightness)) # convert to 16-bit analog value
    return rgb

try:
    while True:
        
    #Begin while Loop reading for a color dial.
        
        redPot=myRed.read_u16()
        greenPot=myGreen.read_u16()        
        bluePot=myBlue.read_u16()   

    #determine the voltage 0-255 (sorry for hardcoded values but specific to the
    #reading my devices were giving me (304,0) and (65535,255), then use the followign formulas to
    # slope M =(y2-y1)/x2-x1) then y-y1= [M](x-x1)
    
        redValue=int(round(((255/65231)*redPot)-(304*(255/65231)),1))
        greenValue=int(round(((255/65231)*greenPot)-(304*(255/65231)),1))
        blueValue=int(round(((255/65231)*bluePot)-(304*(255/65231)),1))
 
 #for fun print out the number of the dial
#        print(f"{redValue:03},{greenValue:03},{blueValue:03}")

        
        if redValue < 0:
            redValue=0
        if greenValue < 0:
            greenValue=0
        if blueValue < 0:
            blueValue=0
            
   #set the duty cycle to the adjusted votage for Red, green, and blue
        redLED.duty_u16(convert_rgb_to_analog(redValue))
        greenLED.duty_u16(convert_rgb_to_analog(greenValue))
        blueLED.duty_u16(convert_rgb_to_analog(blueValue))
            
except KeyboardInterrupt:
    reset_duty_cycles()
    print("Going Down - Turn everything off")

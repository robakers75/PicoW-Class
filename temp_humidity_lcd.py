from machine import Pin
import utime as time
import dht
from lcd1602 import LCD

#####################################################################
#       Temperature and humidy Sensor with lcd Display
#                       Lesson 22 
#
#  Script: This script will read the temperature and humdity, and
#          then use a toggle button to change the display from Celsius
#          and Fahrenheit. Instead of writing this out to the screen,
#          it is now writing this out to an LCD display.
#
#  Date: 06/25/2023
#
#  Enjoy, copy if you like if you feel its usable 
#####################################################################
togglePin=15
dataPin=16
sensorPin= Pin(dataPin,Pin.OUT,Pin.PULL_UP)
sensor=dht.DHT11(sensorPin)
lcd=LCD()
# Setup Array structures to hold the values from the sensor

tempC=0
tempF=0

#setup input toggle button.

toggleButton=Pin(togglePin,Pin.IN,Pin.PULL_UP)
      
# The button read is very fast, so we have to slow down the read. So to do this we need to checck
# the time and wait a few milliseconds
buttonMsWait=0

# trying to find a way to use interupts instead of sequential reads

buttonInterruptFlag=0
displayCelcius=0

# Setup the interrupt handler so that it can toggle the index for
# the displays
#
def buttonInterruptHandler(pin):
    global buttonInterruptFlag, buttonMsWait,displayCelcius
    if ((time.ticks_ms()-buttonMsWait) > 300):
        buttonMsWait=time.ticks_ms()
        buttonInterruptFlag=1
        displayCelcius=not displayCelcius
        
#declare the handler for the button interrupt.
        
toggleButton.irq(trigger=Pin.IRQ_RISING, handler=buttonInterruptHandler)

## notSure, but I had to do a priming read of the sensor, without this
## I kept getting a timeout error. I don't see it in other peoples solution
## So not sure why my environment is special. I tried getting the next
## version of Thonny and this is did not help. So I stuck with this
## as part of the solution

try:
    sensor.measure()
except:
    time.sleep(2)


####################################################################
# Start Main loop
####################################################################

## Wrtie these constants as they never change This will reduce the flash of
## Clearing the whole display. This way we only repleace the changing temp
## and humidity readings

lcd.clear()
lcd.write(0,0,"Temp=")
lcd.write(0,1,"Humidity=")

try:
## while forever ## 
    while True:
        try:
            sensor.measure()
        except:
            time.sleep(2)
            continue
        
        tempReading=sensor.temperature()
        humReading=sensor.humidity()
        tempC=tempReading
        tempF=round(tempReading*(9/5)+32)
        
        messageLine1=" "
        messageLine2=str(humReading)+'%'
        
        if displayCelcius == 0:
            messageLine1=str(tempC)+str(chr(223))+"C"
        else:
            messageLine1=str(tempF)+chr(223)+"F"
        lcd.write(6,0,messageLine1)
        lcd.write(10,1,messageLine2)
        time.sleep(1)
##(END While)##
 
except KeyboardInterrupt:
    print("Going Down")

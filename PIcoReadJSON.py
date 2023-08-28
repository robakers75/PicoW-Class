#############################################################
#                         Lesson 28 
#
#    purpose - Connect to wifi, and then download JSON Data
#
#              The process will find the available networks
#              and then allow the user to select the network
#              and then provide the password. 
#
#    Date : 08/19/2023
#############################################################
# Import needed libaries
from machine import Pin,I2C,UART
from ssd1306 import SSD1306_I2C
import sys
import time
import math
import network
import socket
import urequests
import secrets

#Setup GPS
gb_gpsModule=UART(1,baudrate=9600,tx=Pin(8), rx=Pin(9))
# define display frequency and I2C bus 
i2c=I2C(1,sda=Pin(2),scl=Pin(3),freq=400000)
#Create IDC Object
# 128 colums and 64 Rows
dsp=SSD1306_I2C(128,64,i2c)

#Global working stroage
# Setup Pins 
buttonPin=16
directionPin=17
stepPin=18
# setup button and the direction Pins
myButton=Pin(buttonPin,Pin.IN,Pin.PULL_UP)
myDirection=Pin(directionPin,Pin.IN,Pin.PULL_UP)
myStep=Pin(stepPin,Pin.IN,Pin.PULL_UP)

#Setup the WIFI
wifi=network.WLAN(network.STA_IF)
wifi.active(True)
myWifi=network.WLAN()
## Globle Variables ###
gb_indButtonInterupt=0
gb_previousStep=False
gb_ctr=0
gb_selectedPSWD =[]
gb_SSID=""
gb_PSWD=""
mySSID=[]
gb_debug=False
gb_alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
            'n','o','p','q','r','s','t','u','v','w','x','y','z',
            '0','1','2','3','4','5','6','7','8','9','!','#','$',
            '&','_','A','B','C','D','E','F','G','J','H','I',
            'J','K','L','M','N','O','P','Q','R','S','T','U','V',
            'W','X','Y','Z','*','<']
gb_aqiData=[{"aqicat":"good","aqiRange":{"lowRange":"000","highRange":"050"},"aqiColor":"green","aqiCatnumber":"1","rgb":{"red":"0","green":"000","blue":"999"}},
            {"aqicat":"moderate","aqiRange":{"lowRange":"051","highRange":"100"},"aqiColor":"yellow","aqiCatnumber":"2","rgb":{"red":"0","green":"000","blue":"999"}},
            {"aqicat":"unhealthy for sensitive Groups","aqiRange":{"lowRange":"101","highRange":"150"},"aqiColor":"orange", "aqiCatnumber":"3","rgb":{"red":"0","green":"000","blue":"999"}},
            {"aqicat":"unhealthy","aqiRange":{"lowRange":"151","highRange":"200"},"aqiColor":"red","aqiCatnumber":"1","rgb":{"red":"0","green":"000","blue":"999"}},
            {"aqicat":"very Unhealthy","aqiRange":{"lowRange":"201","highRange":"300"},"aqiColor":"purple","aqiCatnumber":"1","rgb":{"red":"0","green":"000","blue":"999"}},
            {"aqicat":"hazardous","aqiRange":{"lowRange":"301","highRange":"500"},"aqiColor":"maroon","aqiCatnumber":"1","rgb":{"red":"0","green":"000","blue":"999"}}]

########################################################################
# Variables for GPS 
########################################################################
#Store NEMA Sentence
gb_NEMASentence=bytearray(255)
#Store the status of the Satellite
gb_fixStatus=False
#Store GPS Coordinates
gb_latitude=""
gb_longitude=""
gb_Satellites=""
gb_gpsTime=""
buttonMsWait=0
################################################################
#       Common function to blank out IC2 Display
#       and display a message
################################################################
def displayMsg(msg):
    dsp.fill(0)
    dsp.text(msg,0,20)
    dsp.show()
################################################################
#       Common function to track when button on the Encoder is
#       pressed.
################################################################       
def buttonInterruptHandler(pin):
    global gb_indButtonInterupt, buttonMsWait

    if ((time.ticks_ms()-buttonMsWait) > 500):
        buttonMsWait=time.ticks_ms()
        gb_indButtonInterupt=True
        buttonMsWait=0
    
#################################################
#       Scann the networks that you can see
#       orginal source by Charlotte Swift
#################################################
def loadPossibleNetworks(wifi):
    global mySSID
    wifi.active(True)
    networks = wifi.scan()
    ctr=0;
    for net in (networks): 
        nt=net[0].decode()
        ntlen=len(nt)
        if ntlen>0:
            mySSID.append(net[0].decode())
    if gb_debug== True:
        print('number of networks:', len(mySSID))

####################################################
#  loop through the SSID list and select the one
#  the user wants to connect to
####################################################
def selectNetwork():
    global gb_ctr
    ctr=0
    maxRange=len(mySSID)-1
    gb_previousStep=False
    ##BEgin While Loop
    while gb_indButtonInterupt == False:
        if gb_previousStep != myStep.value():
            if myStep.value() == False:
                if myDirection.value() == False:
                    ctr += 1
                else:
                    ctr -=1
            gb_previousStep = myStep.value()
            
        if ctr > maxRange:
            ctr=0
        else:
            if ctr < 0:
                ctr=maxRange
        gb_ctr=ctr      
        displayMsg(mySSID[gb_ctr])
######################################################
#  purpose: Use the encoder wheel to build the
#  password
######################################################
def selectPassword():
    global gb_ctr,gb_indButtonInterupt,gb_selectedPSWD

    maxRange=len(gb_alphabet)-1
    gb_previousStep=False
    ##BEgin While Loop
    while gb_alphabet[gb_ctr] != '*': 
        while gb_indButtonInterupt == False:
            if gb_previousStep != myStep.value():
                if myStep.value() == False:
                    if myDirection.value() == False:
                        gb_ctr -= 1
                    else:
                        gb_ctr +=1
                gb_previousStep = myStep.value()
            
            if gb_ctr > maxRange:
                gb_ctr=0
            else:
                if gb_ctr < 0:
                    gb_ctr=maxRange
                
            dsp.text("Select * to quit bs <", 2,8)
            dsp.fill_rect(0, 36,15,10,0)
            dsp.text(gb_alphabet[gb_ctr],0,36)     
            dsp.show()

            
        gb_indButtonInterupt=False
        if gb_debug == True:
            print(gb_alphabet[gb_ctr])

        message=""
        if gb_alphabet[gb_ctr] !='*':
            if gb_alphabet[gb_ctr] == '<':
                if len(gb_selectedPSWD) > 0:
                    gb_selectedPSWD.pop()
            else:   
                gb_selectedPSWD.append(gb_alphabet[gb_ctr])
                
       #Rebuild the Password array
              
        for n in gb_selectedPSWD:
            message=message+n

        dsp.fill_rect(0, 55,128,10,0);
        dsp.text(message,0,55)
        dsp.show()
    gb_PSSWD=message
    
#####################################################################
#  Declare Interupt Handler
#####################################################################
#declare the handler for the button interrupt.
       
myButton.irq(trigger=Pin.IRQ_RISING, handler=buttonInterruptHandler)

######################################################################
#                  Convert to Degree
# Note: The Latitude and Longitude are not just flow numbers
#       These numbers have to be converted to Degrees and Minutes
#       Also need to make sure that minutes go to 6 digits'
#  I used code from Ahmad Logs youtube video on the GPS
######################################################################
def convertToDegree(RawDegrees):
    RawAsFloat  = float(RawDegrees)
    firstDigits = int(RawAsFloat/100)                   # Degrees
    nextTwoDigits = RawAsFloat - float(firstDigits*100) # Minutes
    converted = float(firstDigits + (nextTwoDigits/60.0))
    converted ='{0:.6f}'.format(converted)              # to 6 decimal places
    return (str(converted))
    
######################################################################
#                 getPositionData
#
#  Purpose: This module will interact with the GPS Module and
#           return the GPS latitude, longitude, satellites, and gpsTime
#           code found at Ahmad Logs youtube 
######################################################################
def getPositionData(gb_gspModule):
    global gb_fixStatus, gb_latitude, gb_longitude, gb_Satellites, gb_gpsTime
    
#Get GPS Data and terminate the loop after 5 Second 
    while True:
        gb_NEMASentence=""
        gb_NEMASentence=str(gb_gpsModule.readline())
        ################################################################
        # The NEMA Sentence have lots of differnt formats
        # I wanted Global Positioning System Fix Data (Time, Position, Elevation)
        # Which is GPGAA. Not sure why, but this is note retured in every sequence of
        # Sample below: 
        #B'$GPGGA,094840.000,2941.8543,N,07232.5745,E1,09,0.9,102.1,M,0.0,M,,*6C\r\n'
        parts=gb_NEMASentence.split(',')
        
        if gb_debug == True:
            print(parts)
            print(len(parts))
            
        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if (parts[1] and parts[2] and parts[3] and parts[5] and parts[6] and parts[7]):
                if gb_debug == True:
                    print("Message Id  :" + parts[0])
                    print("UTC Time    :" + parts[1])
                    print("Lattitude   :" + parts[2])
                    print("N/S         :" + parts[3])
                    print("Longitude   :" + parts[4])
                    print("E/W         :" + parts[5])
                    print("Position Fix:" + parts[6])
                    print("Sat         :" + parts[7])

                #              parts2 = Message ID
                gb_latitude=convertToDegree(parts[2])
                if (parts[3] == 'S'):
                    gb_latitude = '-'+ gb_latitude
                gb_longitude=convertToDegree(parts[4])
                # parts [5] contain 'E' or 'W'
                if (parts[5] == 'W'):
                    gb_longitude = '-' + gb_longitude
                gb_satellites = parts[7]
                if gb_debug == True:
                    print('Longitude',gb_longitude)
                    print('latitude',gb_latitude)
                    lclTime  = int(float(parts[1]))
                    gb_gpsTime=time.localtime(lclTime)
                gb_fixStatus=True
                break
        gb_gspModule.flush()
        time.sleep(2)

                                                                                                                     
######################################################################
#               Main Line
#
#  Purpose: Guide the user throught connecting to the WIFI, and then
#           loop forever getting Weather Data based upon the poition
#           of the GPS sensor
#####################################################################
displayMsg('finding Netwks')
loadPossibleNetworks(myWifi)
time.sleep(2)

### Before we can to anyhing, we have have to get the network ###
dsp.fill(0)
displayMsg('Selecting Netwks')
time.sleep(2)
gb_indButtonInterupt=False
selectNetwork()

dsp.fill(0)
dsp.text(mySSID[gb_ctr],0,1)
dsp.show()
gb_SSID=mySSID[gb_ctr]

#### Build the password
time.sleep(1)
displayMsg('Selecting PW')
gb_ctr=0
gb_indButtonInterupt=False
selectPassword()

# loop until successful
cntr=0
while True:
    wifi.connect(secrets.SSID, secrets.PASSWORD)
    wifiInfo=wifi.ifconfig()
    if wifi.isconnected()==True:
        displayMsg('Connected')
        time.sleep(2)
        break
    else:
        displayMsg('Connecting: '+ str(cntr))
        time.sleep(4)
    cntr += 1
#### End While #####

dsp.fill(0)
dsp.show()
dsp.text(gb_SSID,1,0)
dsp.show()
# doco key B3BDF27F-B23A-4ADB-AF32-083BA0A8B61D
time.sleep(2)
getPositionData(gb_gpsModule)

airQltyRequest='https://api.openweathermap.org/data/2.5/air_pollution?lat=' + gb_latitude + '&lon=' + gb_longitude + '&APPID=' + secrets.apiKey
if gb_debug == True:
    print('RQST=' ,airQltyRequest)  
#headers = {'Content-Type':'application/json','Authorization':'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'}
#airQlty=urequests.get(airQltyRequest,  timeout = (15, 15), headers=headers).json()
airQlty=[{"DateObserved":"2023-08-28 ","HourObserved":8,"LocalTimeZone":"EST","ReportingArea":"Charlottesville","StateCode":"VA","Latitude":38.03,"Longitude":-78.48,"ParameterName":"O3","AQI":19,"Category":{"Number":1,"Name":"Good"}},{"DateObserved":"2023-08-28 ","HourObserved":8,"LocalTimeZone":"EST","ReportingArea":"Charlottesville","StateCode":"VA","Latitude":38.03,"Longitude":-78.48,"ParameterName":"PM2.5","AQI":35,"Category":{"Number":1,"Name":"Good"}}]

###### GEt the last entry in the JSON for latest air Quality
idx_airQlty = (len(airQlty) -1)
if gb_debug == True:
    print('AirQlkty =', airQlty[idx_airQlty]['AQI'])
wrkAQI = int(airQlty[idx_airQlty]['AQI']) 
wrkRed=0
workGreen=0
workBlue=0
for idx in range(0,len(gb_aqiData),1):
    if (wrkAQI >= int(gb_aqiData[idx]['aqiRange']['lowRange']) and wrkAQI <= int(gb_aqiData[idx]['aqiRange']['highRange'])):
        dsp.text(gb_aqiData[idx]['aqiColor'],0,15)
        dsp.show()
        print('red',gb_aqiData[idx]['rgb']['red'])
        print('green',gb_aqiData[idx]['rgb']['green'])
        print('blue',gb_aqiData[idx]['rgb']['blue'])
#### Eventually add RGB LED #######
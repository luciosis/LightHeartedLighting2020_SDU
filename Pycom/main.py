from machine import Pin, RTC
import utime
from LTR329ALS01 import LTR329ALS01
from socket import socket, AF_INET, SOCK_DGRAM
from network import WLAN
import pycom
import machine

ERRORCONNECTIONRESET = 104
ERRORHOSTUNREACHABLE = 113
light_measurement_counter = 0
newColor = ["green", "blue", "red", "white"]
color = "white"
c = 0
ERRORNONETWORK = 118
#######################
WIFISSID = 'SSID'
WIFIPASS = 'PASSWORD'
HOSTIP = 'HOST'
device = 'DEVICE'

######################
intensity = 0
HOSTPORT = 8080
pycom.heartbeat(False)
rtc=RTC()

#whites = [0x000000, 0x191919, 0x323232,0x4B4B4B, 0x646464, 0x7D7D7D, 0x969696, 0xAFAFAF0, 0xC8C8C8, 0xE1E1E1, 0xFFFFFF]
#blues = [0x000000, 0x000019, 0x000032,0x00004B, 0x000064, 0x00007D, 0x000096, 0x0000F0, 0x0000C8, 0x0000E1, 0x0000FF]
#reds = [0x000000, 0x190000, 0x320000,0x4B0000, 0x640000, 0x7D0000, 0x960000, 0xAF0000, 0xC80000, 0xE10000, 0xFF0000]
#greens = [0x000000, 0x001900, 0x003200,0x004B00, 0x006400, 0x007D00, 0x009600, 0x00AF00, 0x00C800, 0x00E100, 0x00FF00]
rtc.ntp_sync("dk.pool.ntp.org")
wlan = WLAN(mode=WLAN.STA)
wlan.mode()
pycom.heartbeat(False)

nets = wlan.scan()
for net in nets:
    if net.ssid == WIFISSID:
        print("Found network")
        wlan.connect(net.ssid, auth=(net.sec, WIFIPASS), timeout=5000)
        while not wlan.isconnected():
            machine.idle()
        print("Connected succesfully")
        break

m_count = 0
s = socket(AF_INET, SOCK_DGRAM)

    

def wifi_connector():
    global s
    if s:
        s.close()

    s = socket(AF_INET, SOCK_DGRAM)
    

def no_wifi():
    net.ssid = wlan.scan() 
    for net in nets:
        if net.ssid == WIFISSID:
            print("Found network")
            wlan.connect(net.ssid, auth=(net.sec, WIFIPASS), timeout=5000)
            while not wlan.isconnected():
                machine.idle()
            print("Connected succesfully")
            break
    
    utime.sleep(1)
    renew_connection()


def send_data(measurement_counter):
    doSocketMessage(measurement_counter)

def renew_connection():
    wifi_connector()
    while True:
        print("Connecting to host")
        try:
            s.connect((HOSTIP, HOSTPORT)) #Change IP and port
            s.setblocking(0)
            print("Connection established")
            send_data(m_count)
        
            break
        except OSError as e:
            if e.args[0] == ERRORNONETWORK:
                print("Lost network")
                no_wifi()
                break
            elif e.args[0] not in [ERRORHOSTUNREACHABLE, ERRORCONNECTIONRESET]:
                raise
            wifi_connector()
            utime.sleep(1)

def doSocketMessage(measurement_counter):
    color = "white"
    c = 0
    light_measurement_counter = 0
    shouldSend = True
    elapsedTime = 0
    while True:
        try:
            measurement_counter += 1
            light = str(lightsensor.light()[0])
            #print(light)

            measurement_date = rtc.now()
            send_time_string = "{}-{}-{} {}:{}:{}".format(measurement_date[0], measurement_date[1], measurement_date[2], measurement_date[3],
                                                            measurement_date[4], measurement_date[5])

            
            s.sendall('{};{};{};{};{};{};{};{}'.format(measurement_counter, send_time_string, light, intensity, color, device, " ", "level").encode('utf-8'))
            #print(send_time_string)
            message = s.recv(4096)
            print(message)   
            if (message != b''):  
                received_data = message.decode("utf_8")
                elements = received_data.split(";")
                if elements[len(elements) - 1] == 'level':
                    received_data = elements[0]
                    print(received_data)
                    pycom.rgbled(int(elements[0]))
                elif elements[len(elements) - 1] == 'light':
                    color = elements[2]
                    rtc.now()
                    utime.timezone(7200)
                    s.sendall('{};{};{};{};{};{}'.format(elements[0], send_time_string, elements[2], device, "recieved", "light").encode('utf-8'))
                
            utime.sleep(1) #Change how often we send
            
            if(elapsedTime >= 1800 and shouldSend):
                #MeasurementCounter, Send_time, color, device name, send/recieve, type
                color = newColor[c]
                s.sendall('{};{};{};{};{};{}'.format(light_measurement_counter, send_time_string, newColor[c] , device, "send", "light").encode('utf-8'))
                elapsedTime = 0
                c+=1
                light_measurement_counter += 1
            
            else:
                elapsedTime += 1
            
            if(c >= 3):
                c = 0
                        
        except OSError as e:
            if e.args[0] not in [ERRORCONNECTIONRESET, ERRORHOSTUNREACHABLE]:
                raise
            print("Lost connection to host")
            renew_connection()
            break


utime.sleep(5)
lightsensor = LTR329ALS01(pysense = None, sda = 'P22', scl = 'P21')
#apin = setup_tempsensor()
#connect_wifi()
no_wifi()


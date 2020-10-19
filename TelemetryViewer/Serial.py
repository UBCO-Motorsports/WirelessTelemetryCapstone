import serial
import time
import csv

candata = serial.Serial(port='COM4', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False,
                        rtscts=False, dsrdtr=False)

serial.Serial.reset_output_buffer(candata)   #clears input

with open('candatatry1.csv', 'w', newline='', encoding='utf8') as csvfile:
    fieldnames = ['RPM', 'Lateral Acc', 'ThrottlePos']          #defining Columns of csv
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()                                        #Writing the headers to csv
    for i in candata:                                           #Reads when data is incoming, timesout when defined
        data = candata.readline()
        data = data.decode('utf-8')
        print(data)
        csvfile.writelines(data)                                #Prints data to csv
    csvfile.close()                                             #Close csv file
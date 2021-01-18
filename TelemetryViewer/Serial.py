import serial, time, csv, datetime

global array1               #Add as many arrays as we want
global array2
global array3
array1 = []                 #Add as many arrays as we want
array2 = []
array3 = []

def trialplz():             #to test if COMx port is open
    try:
        global ser
        ser = serial.Serial(port='COM4', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2,
                            xonxoff=False)
        print("Com port is now open")
        printprompt()

    except IOError:
        print("Com port is not open, Check again? y or n")
        checkport = input()
        if checkport == "y":
            trialplz()
        elif checkport == "n":
            exit()


def printprompt():          #prompt to save or just view incoming data
    print("Would you like to save to cvs???  y or n")
    recordtocvs = input()
    if recordtocvs == "y":
        print("Record and Print Data")
        recandprint()
    elif recordtocvs == "n":
        print("Just Print Data")
        justprint()
    else:
        print("Sorry, that was an invalid entry; y or n?")
        printprompt()


def recandprint():          #code that views,saves to arrays and to csv
    with open('serialcsvdata.csv', 'w', newline='', encoding='utf8') as csvfile:
        t = datetime.datetime.now()
        writer = csv.writer(csvfile, delimiter=' ')
        writer.writerow(['RPM', 'Lateral Acc', 'ThrottlePos', ':', 'Time started:',t.strftime("%H:%M:%S")])
                                            # Writing the headers to csv
        for _ in ser:
            data = ser.readline()
            data = data.decode('utf-8')
            data = data.rstrip()            #gets rid of \n from energia generated code
            dataapp = data.split(',')
            print(dataapp)
            array1.append(dataapp[0])       #writing to arrays
            array2.append(dataapp[1])           #Add as many arrays as we want
            array3.append(dataapp[2])
            writer.writerows([dataapp])     #the actual writing to csv


def justprint():            #code that only views and saves to arrays
    for _ in ser:
        t = datetime.datetime.now()
        data = ser.readline()
        data = data.decode('utf-8')
        data = data.rstrip()  # gets rid of \n from energia generated code
        dataapp = data.split(",")
        print(dataapp)
        array1.append(dataapp[0])           #Add as many arrays as we want
        array2.append(dataapp[1])
        array3.append(dataapp[2])


try:                    #FIRST try to see it the port it open, if not, it goes to excep->trialplz()
    ser = serial.Serial(port='COM4', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2,xonxoff=False)
    # 'timeout' is how long the code will wait for input data until it stops running, want to see if we
            #  can make it something else...
    print("Com port is open")
    serial.Serial.reset_output_buffer(ser)  # clears input
    printprompt()

except:
    trialplz()

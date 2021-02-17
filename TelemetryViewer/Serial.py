import serial, time, csv, datetime
from serial import Serial  # Serial code
from serial import SerialException

dataDict = 0

# TODO 2. Need SEND capability and make sure it works. > can test by making a quick code to make an led blink on
# TODO    Royden's TIVA board. Jan 20

class SerialModule():
    def __init__(self):
        global dataDict
        self.serialConnected = False
        self.arrays = []
        dataDict = {'logged':[]}
        for x in range(16):
            # self.arrays.append([0 for _ in range(200)])
            self.arrays.append([])




    def tryConnectSerial(self, portName):
        if portName == 'Disconnect':
            self.serialChannel.close()
            print('COM disconnected')
        else:
            try:
                # global serialChannel
                # self.serialChannel = serialChannel
                print('try serial')
                self.serialChannel = SerialClass(port=portName, baudrate=9600, bytesize=8, parity='N', stopbits=1,
                                                 timeout=0.2, xonxoff=False)  # TODO Change  timeout to 15 seconds...
                print('COM connected')
                self.serialConnected = True
                return True
            except SerialException:
                # del self
                print("COM failed -> closed")
                self.serialConnected = False
                # self.close() # close instance if failed
                return False

    def getData(self):
        return self.arrays ##############

    def sendCommand(self, command):
        self.serialChannel.write(str(command).encode())  # should work for sending strings

    def recievedataDict(self, data):        #Saves dataDict from Setup page to use for scaling in readSerial()
        global dataDict
        dataDict = data


    def readSerial(self):
        global dataDict

        if self.serialChannel.is_open:
            dataa = self.serialChannel.readline()
            try:
                dataa = dataa.decode('cp1252')
            except:
                dataa = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
            dataa = dataa.rstrip()  # gets rid of \n from energia generated code
            dataapp = dataa.split(",")
        else:
            dataapp = []
            for i in range(16):
                dataapp.append(0)

        for i in range(len(dataDict['logged'])):
            array = self.arrays[i]
            if len(array) >= 200: #TODO set buffer size
                del array[0]
            try:
                if float(dataapp[i]) > 20000:
                    print("Massive raw at index " + str(i))

                value = float(dataapp[i])*float(dataDict['logged'][i]['Scale'])+float(dataDict['logged'][i]['Offset'])
                array.append(value)
            except:
                print("Parse error")
                if (len(array) > 2):
                    array.append(array[len(array)-2])
                else:
                    array.append(0)



class SerialClass(serial.Serial):
    # def __init__(self,port): # , baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10, xonxoff=False
    #     print('init')
    #     super(SerialTest, self).__init__(port=port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10,
    #                                            xonxoff=False)
    def __del__(self):
        print('testing')
        super(SerialClass, self).__del__()

    def close(self):
        print('closing serial')
        super(SerialClass, self).close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('time out ')
        super(SerialClass, self).__exit__(self, exc_type, exc_val, exc_tb)

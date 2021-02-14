import serial, time, csv, datetime
from serial import Serial  # Serial code
from serial import SerialException

dataDict = 0

# TODO 2. Need SEND capability and make sure it works. > can test by making a quick code to make an led blink on
# TODO    Royden's TIVA board. Jan 20
# TODO 4. Scaling Function - to expand or shrink data points
# TODO More to the END, Use Threading for updating graphs, checking serial ports, etc. Or Multiprocessing

class SerialModule():
    def __init__(self):
        # self.array1 = [0 for _ in range(200)]
        # self.array2 = [0 for _ in range(200)]
        # self.array3 = [0 for _ in range(200)]
        # self.array4 = [0 for _ in range(200)]
        # self.array5 = [0 for _ in range(200)]
        # self.array6 = [0 for _ in range(200)]
        # self.array7 = [0 for _ in range(200)]
        # self.array8 = [0 for _ in range(200)]
        # self.array9 = [0 for _ in range(200)]
        # self.array10 = [0 for _ in range(200)]
        # self.array11 = [0 for _ in range(200)]
        # self.array12 = [0 for _ in range(200)]
        # self.array13 = [0 for _ in range(200)]
        # self.array14 = [0 for _ in range(200)]
        # self.array15 = [0 for _ in range(200)]
        # self.array16 = [0 for _ in range(200)]

        self.arrays = []
        for x in range(16):
            # self.arrays.append([0 for _ in range(200)])
            self.arrays.append([])

        # self.arrays = [self.array1, self.array2, self.array3, self.array4, self.array5, self.array6, self.array7, self.array8, self.array9, self.array10, self.array11, self.array12, self.array13, self.array14, self.array15, self.array16] ###
        # self.datadictionary = {}
    # filter0 = rpm
    # filter1 = speed
    # for filter in filters:
    #     sendCommand(filterFormat())

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
                                                 timeout=0.1, xonxoff=False)  # TODO Change  timeout to 15 seconds...
                print('COM connected')
                return True
            except SerialException:
                # del self
                print("COM failed -> closed")
                # self.close() # close instance if failed
                return False

    def getData(self):
        return self.arrays ##############

    def sendCommand(self, command):
        self.serialChannel.write(str(command).encode())  # should work for sending strings

    def recievedataDict(self, data):        #Saves dataDict from Setup page to use for scaling in readSerial()
        global dataDict
        dataDict = data
        # self.datadictionary['logged'] = data['logged']
        # self.datadictionary = data
        # print(len(data["logged"]))
        # print(self.datadictionary)
        # print(dataDict)
        # print(len(self.datadictionary["logged"]))
        # return self.datadictionary

    def readSerial(self):
        global dataDict

        if self.serialChannel.is_open:
            dataa = self.serialChannel.readline()
            dataa = dataa.decode('utf-8')
            dataa = dataa.rstrip()  # gets rid of \n from energia generated code
            dataapp = dataa.split(",")
        else:
            dataapp = []
            for i in range(16):
                dataapp.append(0)
        # self.array1 = self.array1[1:]  # Remove the first y element.
        # self.array2 = self.array2[1:]
        # self.array3 = self.array3[1:]
        # self.array4 = self.array4[1:]
        # self.array5 = self.array5[1:]
        # self.array6 = self.array6[1:]
        # self.array7 = self.array7[1:]  # Remove the first y element.
        # self.array8 = self.array8[1:]
        # self.array9 = self.array9[1:]
        # self.array10 = self.array10[1:]
        # self.array11 = self.array11[1:]
        # self.array12 = self.array12[1:]
        # self.array13 = self.array13[1:]
        # self.array14 = self.array14[1:]
        # self.array15 = self.array15[1:]
        # self.array16 = self.array16[1:]

        for i, array in enumerate(self.arrays):
            if len(array) >= 200: #TODO set buffer size
                del array[0]
            try:
                array.append(float(dataapp[i])*float(dataDict['logged'][i]['Scale'])+float(dataDict['logged'][i]['Offset']))
            except:
                array.append(0)

        # try:
        #     self.array1.append(float(dataapp[0])*float(dataDict['logged'][0]['Scale'])+float(dataDict['logged'][0]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array1.append(0)
        # try:
        #     self.array2.append(float(dataapp[1])*float(dataDict['logged'][1]['Scale'])+float(dataDict['logged'][1]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array2.append(0)
        # try:
        #     self.array3.append(float(dataapp[2])*float(dataDict['logged'][2]['Scale'])+float(dataDict['logged'][2]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array3.append(0)
        # try:
        #     self.array4.append(float(dataapp[3])*float(dataDict['logged'][3]['Scale'])+float(dataDict['logged'][3]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array4.append(0)
        # try:
        #     self.array5.append(float(dataapp[4])*float(dataDict['logged'][4]['Scale'])+float(dataDict['logged'][4]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array5.append(0)
        # try:
        #     self.array6.append(float(dataapp[5])*float(dataDict['logged'][5]['Scale'])+float(dataDict['logged'][5]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array6.append(0)
        # try:
        #     self.array7.append(float(dataapp[6])*float(dataDict['logged'][6]['Scale'])+float(dataDict['logged'][6]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array7.append(0)
        # try:
        #     self.array8.append(float(dataapp[7])*float(dataDict['logged'][7]['Scale'])+float(dataDict['logged'][7]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array8.append(0)
        # try:
        #     self.array9.append(float(dataapp[8])*float(dataDict['logged'][8]['Scale'])+float(dataDict['logged'][8]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array9.append(0)
        # try:
        #     self.array10.append(float(dataapp[9])*float(dataDict['logged'][9]['Scale'])+float(dataDict['logged'][9]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array10.append(0)
        # try:
        #     self.array11.append(float(dataapp[10])*float(dataDict['logged'][10]['Scale'])+float(dataDict['logged'][10]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array11.append(0)
        # try:
        #     self.array12.append(float(dataapp[11])*float(dataDict['logged'][11]['Scale'])+float(dataDict['logged'][11]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array12.append(0)
        # try:
        #     self.array13.append(float(dataapp[12])*float(dataDict['logged'][12]['Scale'])+float(dataDict['logged'][12]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array13.append(0)
        # try:
        #     self.array14.append(float(dataapp[13])*float(dataDict['logged'][13]['Scale'])+float(dataDict['logged'][13]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array14.append(0)
        # try:
        #     self.array15.append(float(dataapp[14])*float(dataDict['logged'][14]['Scale'])+float(dataDict['logged'][14]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array15.append(0)
        # try:
        #     self.array16.append(float(dataapp[15])*float(dataDict['logged'][15]['Scale'])+float(dataDict['logged'][15]['Offset']))  # Add as many arrays as we want
        # except:
        #     self.array16.append(0)

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

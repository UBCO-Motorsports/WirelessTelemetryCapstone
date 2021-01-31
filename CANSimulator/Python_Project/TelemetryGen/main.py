import sys
import csv

# Association of AIM channel with CAN transmission data
# ID, BITOFFSET, SIZE, SCALING, OFFSET
CANDATA = {"ECU_RPM": [864, 0, 2, 1, 0],
            "ECU_ThrottlePos": [864, 4, 2, 0.1, 0],
            "LateralAcc": [0, 0, 0, 0, 0],
            "ECU_OilPress": [0, 0, 0, 0, 0],
            "ECU_Lambda1": [0, 0, 0, 0, 0],
            "ECU_EGTSensor1": [0, 0, 0, 0, 0],
            "ECU_CoolantTemp": [0, 0, 0, 0, 0],
            "Total_Current": [0, 0, 0, 0, 0],
            "OILTEMP": [0, 0, 0, 0, 0],
            "GPS_Speed": [0, 0, 0, 0, 0],
            "NA": [0, 0, 0, 0, 0]
           }

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Not enough arguments!")
    outputdict = {"": [0.1, 0.1, 0.1, 0.1]}
    outputdict.clear()
    for key in CANDATA.keys():
        with open(sys.argv[1]) as csvfile:
            reader = csv.DictReader(csvfile)
            if key in reader.fieldnames:
                print(key + " found")
                for row in reader:
                    if key not in outputdict:
                        outputdict[key] = CANDATA[key]
                    outputdict[key].append(float(row[key]))

    # Now parse dictionary into C float[][] array
    outputFile = open(sys.argv[2], "w")
    outputFile.write("static const float carData[" + str(len(outputdict)) + "][" + str(len(outputdict[list(outputdict.keys())[0]])) + "] = ")
    finalString = "{"
    i = 1
    for name, metric in outputdict.items():
        finalRow = "{"
        j = 1
        for value in metric:
            finalRow += str(value)
            if j < len(metric):
                finalRow += ","
            j += 1
        finalRow += "}"
        if i < len(outputdict):
            finalRow += ","
        i += 1
        finalRow += "\r\n"
        finalString += finalRow
    finalString += "};"
    outputFile.write(finalString)
    outputFile.close()
    print("Success!")


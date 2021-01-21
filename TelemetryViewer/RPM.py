
import sys
from PyQt5 import QtWidgets, QtCore,QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu

from RPMroot import Ui_Form

RPM = 0
resizeval=0


class RPMScreen(QtWidgets.QWidget):
    def __init__(self, parentWidget):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.animate(0)

        self.type = 'dial'
        self.parentWidget = parentWidget

        self.dial_size = self.ui.frame

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.accellerate)
        self.timer.start(15)

        # self.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        newAct = menu.addAction("Test")
        quitAct= menu.addAction("Quit")
        action= menu.popup(self.mapToGlobal(event.pos()))
        quitAct.triggered.connect(self.close)


    def accellerate (self):
        global RPM
        value=RPM

        self.animate(value)
        if RPM > 17000:
            self.timer.stop()

            self.close()
        RPM += 20


    def resizeEvent(self, a0: QtGui.QResizeEvent):
        height=self.height()
        width=self.width()
        if height>width:
            length=width
        else:
            length=height
        self.ui.frame.setGeometry(QtCore.QRect(0, 0, length, length))
        self.ui.frame_2.setGeometry(QtCore.QRect(5, 5, length-10,length-10))
        scircle = """QFrame{
                        border-radius: {Value};
                        background-color: rgb(247,247,247);
                        }"""
        scircle = scircle.replace("{Value}", str(int((length-10)/2)))
        self.ui.frame_2.setStyleSheet(scircle)
        self.ui.frame_3.setGeometry(QtCore.QRect(0, 0, length,length))
        bcircle = """QFrame{
                        border-radius: {Value};
                        background-color: rgb(0,0,0);
                        }"""
        bcircle = bcircle.replace("{Value}", (str(int((length)/2))))
        self.ui.frame_3.setStyleSheet(bcircle)
        self.ui.frame_4.setGeometry(QtCore.QRect(0, 0, length,length))
        smallneedle = QtGui.QPixmap("QT Images/needle3.png")
        smallneedle=smallneedle.scaled(length,length, Qt.KeepAspectRatio, Qt.FastTransformation)
        t = QtGui.QTransform()
        t.rotate(resizeval)
        smallneedle=smallneedle.transformed(t)
        self.ui.Needle.setGeometry(QtCore.QRect(0, 0, length,length))
        self.ui.Needle.setPixmap(smallneedle)

        tach = QtGui.QPixmap("QT Images/Tachlinesr.png")
        tach = tach.scaled(length+30, length+30, Qt.KeepAspectRatio,Qt.FastTransformation)
        self.ui.label.setGeometry(-15,-15,length+30,length+30)
        self.ui.label.setPixmap(tach)


        numbers = QtGui.QPixmap("QT Images/RPM numbers resize.png")
        numbers = numbers.scaled(length+20, length+20, Qt.KeepAspectRatio,Qt.FastTransformation)
        self.ui.label_2.setGeometry(-10, -45, length+30, length+30)
        self.ui.label_2.setPixmap(numbers)
        self.ui.RPMtext.setGeometry(QtCore.QRect(0, length*250/320, length, 50))

        pointer = QtGui.QPixmap("QT Images/Pointer2.png")
        pointer = pointer.scaled(length, length, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.ui.label_3.setGeometry(0, 5, length, length)
        self.ui.label_3.setPixmap(pointer)
        self.ui.RPMtext.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.frame_4.raise_()
        self.ui.frame_3.raise_()
        self.ui.frame_2.raise_()
        self.ui.label.raise_()
        self.ui.label_2.raise_()
        self.ui.Needle.raise_()
        self.ui.RPMtext.raise_()
        self.ui.label_3.raise_()


    def animate(self,value):
        global RPM
        global resizeval
        global needleimage
        value=RPM
        htmlText="{Value}"
        newHtml=htmlText.replace("{Value}",str(value))
        self.ui.RPMtext.setText(newHtml)

        t = QtGui.QTransform()
        # -222 and 45
        if value>16000:
            value=16000
        if value<0:
            value=0
        value=reMap(RPM,16000,0,253,-15)
        resizeval = value
        t.rotate(value)
        # load your image
        image = QtGui.QImage("QT Images/needle3.png")
        pixmap = QtGui.QPixmap.fromImage(image)
        # rotate the pixmap
        rotated_pixmap = pixmap.transformed(t)
        self.ui.Needle.setPixmap(rotated_pixmap)


def reMap(value, maxInput, minInput, maxOutput, minOutput):
    value = maxInput if value > maxInput else value
    value = minInput if value < minInput else value

    inputSpan = maxInput - minInput
    outputSpan = maxOutput - minOutput

    scaledThrust = float(value - minInput) / float(inputSpan)

    return minOutput + (scaledThrust * outputSpan)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RPMScreen()
    sys.exit(app.exec_())

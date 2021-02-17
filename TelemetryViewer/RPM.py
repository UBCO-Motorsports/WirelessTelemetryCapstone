
import sys
from PyQt5 import QtWidgets, QtCore,QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu

from RPMroot import Ui_Form

RPM = 0
newneedle=0


class RPMGauge(QtWidgets.QWidget):
    def __init__(self, parentwidget):
        QtWidgets.QWidget.__init__(self)
        self.parentwidget = parentwidget
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.animate(0)
        self.highlighted = False

        self.dial_size = self.ui.frame

        self.type = 'RPM Gauge'
        self.yData = []

        # self.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        newAct = menu.addAction("Edit Data")
        newAct.triggered.connect(lambda: self.parentwidget.configMenuCalled(self))
        quitAct = menu.addAction("Quit")
        action = menu.popup(self.mapToGlobal(event.pos()))
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
        global newneedle
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
        scircle = scircle.replace("{Value}", str(int(int((length-10)/2))))
        self.ui.frame_2.setStyleSheet(scircle)
        self.ui.frame_3.setGeometry(QtCore.QRect(0, 0, length,length))
        bcircle = """QFrame{
                        border-radius: {Value};
                        background-color: rgb(0,0,0);
                        }"""
        bcircle = bcircle.replace("{Value}", (str(int(int((length)/2)))))
        self.ui.frame_3.setStyleSheet(bcircle)
        self.ui.frame_4.setGeometry(QtCore.QRect(0, 0, length,length))

        self.ui.Needle.setGeometry(0, 0, length,length)
        needle=QtGui.QPixmap("QT Images/needle3.png")
        needle=needle.scaled(length,length,Qt.KeepAspectRatio, Qt.FastTransformation)
        newneedle=needle

        tach = QtGui.QPixmap("QT Images/Tachlinesr.png")
        tach = tach.scaled(length*1.2, length*1.2, Qt.KeepAspectRatio,Qt.FastTransformation)
        self.ui.label.setGeometry(-length*0.1,-length*0.1,length*1.2,length*1.2)
        self.ui.label.setPixmap(tach)


        numbers = QtGui.QPixmap("QT Images/RPM numbers resize.png")
        numbers = numbers.scaled(length*1.1, length*1.1, Qt.KeepAspectRatio,Qt.FastTransformation)
        self.ui.label_2.setGeometry(-length*0.05, -length*0.15, length*1.1, length*1.1)
        self.ui.label_2.setPixmap(numbers)

        self.ui.RPMtext.setGeometry(0, length/2.5,length,length)
        self.ui.RPMtext.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.RPMtext.setFont(QtGui.QFont('Bahnschrift SemiCondensed',length/15))

        pointer = QtGui.QPixmap("QT Images/Pointer2.png")
        pointer = pointer.scaled(length, length, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.ui.label_3.setGeometry(0, 5, length, length)
        self.ui.label_3.setPixmap(pointer)
        self.ui.RPMtext.setAlignment(QtCore.Qt.AlignCenter)

        if self.highlighted:
            self.ui.frame_3.setStyleSheet('border: 3px solid #00ff00;')

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
        global newneedle
        # value=int(RPM)
        RPM = value
        htmlText="{Value}"
        newHtml=htmlText.replace("{Value}",str(int(value)))
        self.ui.RPMtext.setText(newHtml)

        t = QtGui.QTransform()
        # -222 and 45
        if value>16000:
            value=16000
        if value<0:
            value=0
        value=reMap(RPM,16000,0,253,-15)
        t.rotate(value)
        if newneedle is not 0:
            pixmap=newneedle
        else:
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
    window = RPMGauge()
    sys.exit(app.exec_())

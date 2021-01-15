
import sys
from PyQt5 import QtWidgets, QtCore,QtGui
from PyQt5.QtWidgets import QMenu

from RPMroot import Ui_Form

RPM = 0


class SplashScreen(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.animate(0)

        self.dial_size = self.ui.frame

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.accellerate)
        self.timer.start(15)

        self.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        newAct = menu.addAction("Test")
        quitAct= menu.addAction("Quit")
        action= menu.popup(self.mapToGlobal(event.pos()))
        if action == quitAct:
            self.close()

    def accellerate (self):
        global RPM
        value=RPM

        self.animate(value)
        if RPM > 17000:
            self.timer.stop()

            self.close()
        RPM += 0


    def animate(self,value):
        global RPM
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
    window = SplashScreen()
    sys.exit(app.exec_())

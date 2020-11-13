import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence,
                           QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *

# GUI File

from RPMroot import RPMQT

RPM = 0


class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = RPMQT()
        self.ui.setupUi(self)
        self.animate(0)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.accellerate)
        self.timer.start(15)

        self.show()
    def accellerate (self):
        global RPM
        value=RPM

        self.animate(value)
        if RPM > 17000:
            self.timer.stop()

            self.close()
        RPM += 30


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
        image = QtGui.QImage("needle3.png")
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
    app = QApplication(sys.argv)
    window = SplashScreen()
    sys.exit(app.exec_())

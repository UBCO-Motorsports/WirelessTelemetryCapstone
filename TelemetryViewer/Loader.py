import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence,
                           QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *

# GUI File

from TelemetryLoader import Ui_SplashScreen


class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui= Ui_SplashScreen()
        self.ui.setupUi(self)

        self.progressbarVal(0)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.shadow=QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0,0,0,100))
        self.ui.Circularvaluebg.setGraphicsEffect(self.shadow)

        self.show()
        self.counter = 0

    def progress (self):
        self.progressbarVal(self.counter)

        if self.counter > 100:
            self.close()

        self.counter += 0.5

    def progressbarVal(self,value):
        styleSheet = """
        QFrame{
            border-radius: 150px;
            background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} rgba(0, 85, 255, 255));
        }
        """
        progress= (100-value)/100.0

        stop_1=str(progress-0.001)
        stop_2=str(progress)

        newStylesheet=styleSheet.replace("{STOP_1}",stop_1).replace("{STOP_2}",stop_2)

        self.ui.Circularvalue.setStyleSheet(newStylesheet)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    window = SplashScreen()
    sys.exit(app.exec_())

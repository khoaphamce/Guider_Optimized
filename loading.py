from PyQt5.QtGui     import QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QLabel, QDesktopWidget
from PyQt5 			 import QtCore



class GifFrame(QLabel):
	def __init__(self, parent):
		QLabel.__init__(self)
		self.Parent = parent
		self.setLineWidth(10)
		self.setMidLineWidth(10)

		self.DaGif = QMovie("loading.gif")
		
		self.lblGifHldr = QLabel()
		self.lblGifHldr.setMovie(self.DaGif)

		self.DaGif.start()
		self.Parent.IsOn = True

		HBox = QHBoxLayout()
		HBox.addStretch(1)
		HBox.addWidget(self.lblGifHldr)
		HBox.addStretch(1)
		
		self.setLayout(HBox)
		
class CenterPanel(QWidget):
	def __init__(self, parent):
		QWidget.__init__(self)
		self.Parent = parent
		self.IsOn = False
		
		self.GifView = GifFrame(self)

		VBox = QVBoxLayout()
		VBox.addWidget(self.GifView)

		
		self.setLayout(VBox)


class MainUI(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.setWindowTitle('Framed It')
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)
		self.setWindowModality(QtCore.Qt.ApplicationModal)
		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		
		
		WinLeft = 550; WinTop = 250; WinWidth = 550; WinHigh = 550
		self.setGeometry(WinLeft, WinTop, WinWidth, WinHigh)

		self.CenterPane = CenterPanel(self)
		self.setCentralWidget(self.CenterPane)
		qtRectangle = self.frameGeometry()
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())

if __name__ == "__main__":
	MainEventHandler = QApplication([])

	MainApplication = MainUI()
	MainApplication.show()
	
	MainEventHandler.exec()
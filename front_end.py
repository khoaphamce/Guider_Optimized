import sys, os
from config import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QEvent, QVariant, QFile, QTextStream, QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QMovie, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QTableView, QHeaderView, QWidget, QLabel, QMessageBox, QScroller, QAbstractItemView, QScrollerProperties
from maingui import Ui_MainWindow
from MainBackend import *
import time
from qr import Ui_Qr
from loading import MainUI
import threading



#PHOTO VIEWER && ZOOM IMAGE
class PhotoViewer(QtWidgets.QGraphicsView):
	photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

	def __init__(self, parent):
		super(PhotoViewer, self).__init__(parent)
		self._zoom = 0
		self._empty = True
		self._scene = QtWidgets.QGraphicsScene(self)
		self._photo = QtWidgets.QGraphicsPixmapItem()
		self._scene.addItem(self._photo)
		self.setScene(self._scene)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
		self.setFrameShape(QtWidgets.QFrame.NoFrame)

	def hasPhoto(self):
		return not self._empty

	def fitInView(self, scale=True):
		rect = QtCore.QRectF(self._photo.pixmap().rect())
		if not rect.isNull():
			self.setSceneRect(rect)
			if self.hasPhoto():
				unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
				self.scale(1 / unity.width(), 1 / unity.height())
				viewrect = self.viewport().rect()
				scenerect = self.transform().mapRect(rect)
				factor = min(viewrect.width() / scenerect.width(),
							 viewrect.height() / scenerect.height())
				self.scale(factor, factor)
			self._zoom = 0

	def setPhoto(self, pixmap=None):
		self._zoom = 0
		if pixmap and not pixmap.isNull():
			self._empty = False
			self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
			self._photo.setPixmap(pixmap)
		else:
			self._empty = True
			self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
			self._photo.setPixmap(QtGui.QPixmap())
		self.fitInView()
	
	#MOUSE EVENT
	def wheelEvent(self, event):
		if self.hasPhoto():
			if event.angleDelta().y() > 0:
				factor = 1.25
				self._zoom += 1
			else:
				factor = 0.8
				self._zoom -= 1
			if self._zoom > 0:
				self.scale(factor, factor)
			elif self._zoom == 0:
				self.fitInView()
			else:
				self._zoom = 0

	def toggleDragMode(self):
		if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
			self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
		elif not self._photo.pixmap().isNull():
			self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

	def mousePressEvent(self, event):
		if self._photo.isUnderMouse():
			self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
		super(PhotoViewer, self).mousePressEvent(event)
	#TOUCH EVENT
	def event(self,e):
		if (e.type() == QEvent.Gesture):
			return self.gestureEvent(e)
		return super(PhotoViewer,self).event(e)
		 
	def gestureEvent(self,event):
		pinch = event.gesture(Qt.PinchGesture)
		if pinch:
			self.pinchTriggered(pinch)
		return True
		 
	def pinchTriggered(self,gesture):
		self.scaleImage(gesture.scaleFactor())

	def scaleImage(self, factor):
		if self.hasPhoto():
			if factor > 1:
				factor = 1.05
				self._zoom += 1
			else:
				factor = 0.95
				self._zoom -= 1
			if self._zoom > 0:
				self.scale(factor, factor)
			elif self._zoom <= 0:
				self.fitInView()
			else:
				self._zoom = 0
	
#QR INTERFACE
class qrscreen(QMainWindow):
	
	def __init__(self):
		QMainWindow.__init__(self)
		self.qr = Ui_Qr()
		self.qr.setupUi(self)
		self.setWindowTitle('QR screen')
		self.setWindowIcon(QIcon("logo/iconguider.ico"))
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint)
		self.setWindowModality(QtCore.Qt.ApplicationModal)
		self.qr.qrcodeui.clicked.connect(self.qr_image)
		self.qr.cancel.clicked.connect(self.qr_out)
		self.qr.cancel2.clicked.connect(self.qr_out)

	def qr_image(self):
		self.upload_work = UploadThreadQr()
		self.loading = MainUI()
		self.loading.show()

		self.upload_work.start()
		
		self.upload_work.finished.connect(self.display_qr)
		
			
	def display_qr(self):
		global u
		if u == 0:
			self.loading.close()
			self.errorMessage()
			return 0
		pixmap = QtGui.QPixmap('QrCode.jpg')
		resize_pixmap = pixmap.scaled(211, 211, Qt.KeepAspectRatio, Qt.FastTransformation)
		self.qr.qrimage.setPixmap(resize_pixmap)
		self.qr.stackedWidget.setCurrentIndex(1)
		self.loading.close()
	
	def qr_out(self):
		self.close()

	def errorMessage(self):
		msgBox = QMessageBox()
		msgBox.setStyleSheet("font-size: 25px; QPushButton{ width:125px; font-size: 20px; }")
		msgBox.setWindowIcon(QIcon('logo/iconguider.ico'))
		msgBox.setIcon(QMessageBox.Warning)
		msgBox.setText("Bản đồ chưa được hiển thị")
		msgBox.setWindowTitle("Lỗi")
		msgBox.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
		msgBox.setStandardButtons(QMessageBox.Ok)
		returnValue = msgBox.exec()
		if returnValue == QMessageBox.Ok:
			pass

class UploadThreadQr(QThread):
	def run(self):
		try:
			global start, end, u
			UploadGetLink('ToDrawMap/Path.jpg',start, end)
			u = 1 
		except:
			u=0
		
		
#-------------------##---------Main Window------------##-------------------------#
class MainWindow(QtWidgets.QWidget):
	
	def __init__(self):
		#INIT
		super(MainWindow, self).__init__()
		self.main_ui = QMainWindow()
		self.ui = Ui_MainWindow()
		self.setWindowTitle('Main Screen')
		self.main_ui.setWindowIcon(QIcon("logo/iconguider.ico"))
		self.ui.setupUi(self.main_ui)
		self.ui.stackedWidget.setCurrentWidget(self.ui.main)
		self.msgBox = QMessageBox()
		self.loading = MainUI()
		
		
				#-----------------#
		#PUBLISH IMAGE
		self.viewer = PhotoViewer(self)
		self.viewer.grabGesture(Qt.PinchGesture)
		self.ui.gridLayout_14.addWidget(self.viewer, 0, 0, 1, 2)

				#-----------------#
		#CONFIG FOR TEXT INFORMATION
			#Disable hightlight text
		self.ui.guide.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
		self.ui.textBrowser.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
		self.ui.info_room.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
			#Scroller
		self.scroller_text(self.ui.info_room)
		self.scroller_text(self.ui.guide)
		self.scroller_text(self.ui.textBrowser)
				#-----------------#
		#CONFIG FOR TABLE VIEW
			#Scroller
		self.scroller(self.ui.room_building) 
		
			#Disable highlight cell
		self.ui.room_building.setSelectionMode(QAbstractItemView.SingleSelection)
		self.ui.room_building.setSelectionBehavior(QAbstractItemView.SelectRows)
			
			#Hide header
		self.ui.room_building.setStyleSheet('font-size: 35px;')
		self.ui.room_building.verticalHeader().setDefaultSectionSize(65)
		self.ui.room_building.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
		self.ui.room_building.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.ui.room_building.horizontalHeader().hide()
		self.ui.room_building.verticalHeader().hide()
	
				#-----------------#
		#BUTTON
		self.ui.click_to_search.clicked.connect(self.search)
		self.ui.backbutton1.clicked.connect(self.main_screen)
		self.ui.start_lookup.clicked.connect(self.path_finding)
		self.ui.start_lookup_2.clicked.connect(self.information)
		self.ui.backbutton2.clicked.connect(self.search)
		self.ui.find_path.clicked.connect(self.path_finding)
		self.ui.refresh.clicked.connect(self.refresh)
		self.ui.send_image.clicked.connect(self.image_tranfer)
		
		#SIGNAL CONNECT IN SEARCH BAR
		self.varibility = 0
		self.ui.departure.setProperty("keyboard", True)
		self.ui.destination.setProperty("keyboard", True)
		self.ui.departure.focus_in_signal.connect(self.focus_in)
		self.ui.destination.focus_in_signal.connect(self.focus_out)
	
	#PAGE MAIN SCREEN (WITH MAP)
	def main_screen(self):
		self.ui.stackedWidget.setCurrentIndex(0)
		self.ui.tab_alt.setCurrentIndex(0)

	def refresh(self):
		global start, end
		maps = cv2.imread('ToDrawMap/ToDrawMap.jpg')
		cv2.imwrite('ToDrawMap/Path.jpg', maps)
		pixmap = QtGui.QImage(maps.data, maps.shape[1], maps.shape[0], maps.strides[0], QtGui.QImage.Format_RGB888).rgbSwapped()
		pixmap = QtGui.QPixmap.fromImage(pixmap)
		self.viewer.setPhoto(QtGui.QPixmap(pixmap))
		start ='bachkhoa'
		end = 'map'
		self.ui.departure.setText(DEFAULT_PLACE)
		self.ui.destination.setText('')

	def image_tranfer(self):
		self.tranfer = qrscreen()
		self.tranfer.show()
		
	#PAGE SEARCH	
	def search(self):
		self.ui.stackedWidget.setCurrentWidget(self.ui.search_bar)
		buildings = BUILDING_LIST
		model = QStandardItemModel(len(buildings), 1)
		for row, building in enumerate(buildings):
			item = QStandardItem(building)
			model.setItem(row, 0, item)
		filter_proxy_model = QSortFilterProxyModel()
		filter_proxy_model.setSourceModel(model)
		filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
		filter_proxy_model.setFilterKeyColumn(0)
		
		#STYLE SHEET OF SEARCH BAR
		self.ui.destination.setStyleSheet('font-size: 25px; height: 40px;')
		self.ui.destination.textChanged.connect(filter_proxy_model.setFilterRegExp)
		self.ui.departure.setStyleSheet('font-size: 25px; height: 40px;')
		self.ui.departure.textChanged.connect(filter_proxy_model.setFilterRegExp)
		
		#NO EDIT VALUE IN TABLE VIEW
		self.ui.room_building.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.ui.room_building.setModel(filter_proxy_model)
		self.ui.room_building.clicked.connect(self.cell_was_clicked)

	#PAGE INFORMATION
	def information(self):
		room = self.ui.destination.text().upper()
		data = f"building/data/{room}.html"
		image = f"building/room_images/{room}.jpg"
		if not (QFile.exists(data) | QFile.exists(image))  :
			self.msgBox.setText("Chưa có dữ liệu về địa điểm")
			self.errorMessage()
			return -1
		f = QFile(data)
		f.open(QFile.ReadOnly|QFile.Text)
		istream = QTextStream(f)
		self.ui.info_room.setHtml(istream.readAll())
		f.close()
		pixmap = QtGui.QPixmap(image)
		pixmap_resized = pixmap.scaled(1024, 756, QtCore.Qt.KeepAspectRatio)
		self.ui.image_room.setPixmap(pixmap_resized)
		self.ui.stackedWidget.setCurrentWidget(self.ui.page_info)
		return 0

		
#...................SOME METHODS SUPPORT FOR OPERATION......................# 
	#FUNCTIONS SEARCH PAGE
		#Check search bar whether it is focused
	def focus_in(self):
		self.varibility = 1	

	def focus_out(self):
		self.varibility = 0

		#Get place in clicked cell
	def cell_was_clicked(self):
		point = self.varibility
		index = self.ui.room_building.selectionModel().currentIndex()
		value = index.sibling(index.row(),index.column()).data()
		if point == 1 :
			self.ui.departure.setText(value)
			point = 0
		   
		else:
			self.ui.destination.setText(value)

		#Algorithm for find path
	def path_finding(self):
		try:
			global start, end
			start = self.ui.departure.text()
			if start is '': 
				start = DEFAULT_PLACE
				self.ui.departure.setText(DEFAULT_PLACE)
			end = self.ui.destination.text()
			route, Detail = FindPath(start, end)
			route = QtGui.QImage(route.data, route.shape[1], route.shape[0], route.strides[0], QtGui.QImage.Format_RGB888).rgbSwapped()
			route = QtGui.QPixmap.fromImage(route)
			self.viewer.setPhoto(route)
			self.main_screen()
		except:
			self.msgBox.setText("Không tìm thấy địa điểm bạn nhập")
			self.errorMessage()

	#SCROLLER
	def scroller(self, view):
		scroller = QScroller.scroller(view)
		view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
		view.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
		properties = QScroller.scroller(scroller).scrollerProperties()
		overshootPolicy = QVariant((QScrollerProperties.OvershootAlwaysOff))
		properties.setScrollMetric(QScrollerProperties.VerticalOvershootPolicy, overshootPolicy)
		scroller.setScrollerProperties(properties)
		properties.setScrollMetric(QScrollerProperties.HorizontalOvershootPolicy, overshootPolicy)
		scroller.setScrollerProperties(properties)
		scroller.grabGesture(view, QScroller.TouchGesture)
		scroller.grabGesture(view, QScroller.LeftMouseButtonGesture)
	
	def scroller_text(self, text):
		scroller = QScroller.scroller(text)
		text.verticalScrollBar().setValue(text.verticalScrollBar().maximum())
		text.horizontalScrollBar().setValue(text.horizontalScrollBar().maximum())
		properties = QScroller.scroller(scroller).scrollerProperties()
		overshootPolicy = QVariant((QScrollerProperties.OvershootAlwaysOff))
		properties.setScrollMetric(QScrollerProperties.VerticalOvershootPolicy, overshootPolicy)
		scroller.setScrollerProperties(properties)
		properties.setScrollMetric(QScrollerProperties.HorizontalOvershootPolicy, overshootPolicy)
		scroller.setScrollerProperties(properties)
		scroller.grabGesture(text, QScroller.TouchGesture)
		scroller.grabGesture(text, QScroller.LeftMouseButtonGesture)

	#ERROR BOX
	def errorMessage(self):
		self.msgBox.setStyleSheet("font-size: 25px; QPushButton{ width:125px; font-size: 20px; }")
		self.msgBox.setWindowIcon(QIcon('logo/iconguider.ico'))
		self.msgBox.setIcon(QMessageBox.Warning)
		self.msgBox.setWindowTitle("Lỗi")
		self.msgBox.setStandardButtons(QMessageBox.Ok)
		returnValue = self.msgBox.exec()
		if returnValue == QMessageBox.Ok:
			pass

#__________________SCREEN SHOW_________________#			 
	def show(self):

		self.main_ui.showMaximized()
		
		#self.main_ui.showFullScreen()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	main_win = MainWindow()
	main_win.show()
	sys.exit(app.exec_())
#______________________End__________________________#

 


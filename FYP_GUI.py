import RPi.GPIO as GPIO
import time,cv2, sys, EasyPySpin
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QPushButton, QMessageBox, QGridLayout, QLineEdit,QDesktopWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from numpy import ndarray
from PyQt5 import QtCore
global detect
detect = False
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(ndarray)
    productIds = [[],[1],[2],[3],[4],[5],[6],[7],[8],[9]]
    productlist = { 1: "Surf",2: "Lipton Tea",3: "Vim Bar",4: "Dove",5: "Lux",6: "Bottle",7: "Biscuit box",8: "Cream",9: "Toys"}
    #Setting which product should be sort
    product = 1
    selectedP = 1
    def __init__(self):
        super().__init__()
        self.cam= EasyPySpin.VideoCapture(0)
        #Setting Exposure of camera view 
        self.cam.set(cv2.CAP_PROP_EXPOSURE, -1)
        self.cam.set(cv2.CAP_PROP_GAIN, -1) 
        self._run_flag = True
        self._product_flag = True

    def run(self):
        global detect
        # capture from web cam
        GPIO.output(22,True)
        while True:
            success, img =self.cam.read()
            if success: 
                img1 = cv2.flip(img, 1)   
                self.change_pixmap_signal.emit(img1)
                img=cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

                #Aruco Markers Detection
                arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
                arucoParams = cv2.aruco.DetectorParameters_create()
                (corners,id,matri) = cv2.aruco.detectMarkers(img, arucoDict, parameters=arucoParams)
                # print(id)
                if id:
                    self.product = id[0][0]
                    detect = True            
                    if id==self.productIds[self.selectedP]:
                        GPIO.output(22,False)
                        print("Signal Generated")
                        time.sleep(0.2)
        
        # shut down capture system
        self.cam.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision Based High Speed Sorting System")
        self.setWindowIcon(QtGui.QIcon('download.png'))
        self.setStyleSheet("background-color: #002366")
        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()
        self.fg = self.frameGeometry()
        self.des = QDesktopWidget().availableGeometry().topLeft()
        self.fg.moveTopLeft(self.des)
        self.move(self.fg.topLeft())
        self.display_width = 720
        self.display_height = 680
        self.setMaximumSize(720,680)
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width, self.display_height)

        # create a vertical box layout and add the two labels
        # Font and Size
        self.Font = "Times font"
        self.fontSize = 14
        myFont_Bold = QtGui.QFont()
        myFont_Bold.setBold(True)
        
        # create a text labels
        self.title = QLabel('Vision Based High Speed Sorting System')
        self.title.setStyleSheet("QLabel {background-color:#0C6DE8; color: white;}")
        self.title.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.title.setAlignment(Qt.AlignCenter)

        self.cameraView = QLabel('Camera View')
        self.cameraView.setStyleSheet("QLabel {background-color:white; color: #002366;}")
        self.cameraView.setFont(QtGui.QFont(self.Font,self.fontSize))
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.title)
        vbox.addWidget(self.cameraView)
        vbox.addWidget(self.image_label)


        # Create a grid layout 
        self.grid_box = QGridLayout()
        self.toSort_label = QLabel(self)
        self.toSort_label.setText("Which product you want to sort?")
        self.toSort_label.setStyleSheet("QLabel {background-color: #0C6DE8; color: white;}")
        self.toSort_label.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.grid_box.addWidget(self.toSort_label, 0, 0, 1, 1)
        self.toSort_text = QLineEdit(self)
        self.toSort_text.setStyleSheet("QLineEdit {background-color: #FFFFFF; color: black;}")
        self.toSort_text.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.toSort_text.setPlaceholderText("Enter Number between 1 to 9")
        self.grid_box.addWidget(self.toSort_text, 0, 1, 1, 1)
        #Submit QLabel and QButton
        self.Enter = QLabel(self)
        self.Enter.setText("Press Submit")
        self.Enter.setStyleSheet("QLabel {background-color: #0C6DE8; color: white;}")
        self.Enter.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.grid_box.addWidget(self.Enter, 1, 0, 1, 1)
        self.submit_button = QPushButton(self)
        self.submit_button.setText("Submit")
        self.submit_button.setStyleSheet("QPushButton {background-color: green ; color: white; border-color: darkgreen ; border-style: outset; border-width: 2px ; padding: 4px}")
        self.submit_button.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.submit_button.clicked.connect(self.submit)
        self.grid_box.addWidget(self.submit_button, 1, 1, 1, 1)
        #QLabels
        self.sorted_label = QLabel(self)
        self.sorted_label.setText("Product to be sorted")
        self.sorted_label.setStyleSheet("QLabel {background-color: #0C6DE8; color: white;}")
        self.sorted_label.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.grid_box.addWidget(self.sorted_label, 2, 0, 1, 1)
        self.toSorted = QLabel(self)
        self.toSorted.setText(f"Default selected product is {self.thread.productlist.get(self.thread.selectedP)}")
        self.toSorted.setStyleSheet("QLabel {background-color:white; color: black;}")
        self.toSorted.setFont(QtGui.QFont(self.Font,self.fontSize)) 
        self.grid_box.addWidget(self.toSorted, 2, 1, 1, 1)
        self.detected = QLabel(self)
        self.detected.setStyleSheet("QLabel {background-color: #0C6DE8; color: white;}")
        self.detected.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.detected.setText("Detected product")
        self.grid_box.addWidget(self.detected, 3, 0, 1, 1)
        self.detected_name = QLabel(self)
        self.detected_name.setStyleSheet("QLabel {background-color: white; color: green;}")
        self.detected_name.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.grid_box.addWidget(self.detected_name, 3, 1, 1, 1)
        # Closing button
        self.close_button =  QPushButton(self)
        self.close_button.setText("Close Application")
        self.close_button.setStyleSheet("QPushButton {background-color: #8b0000 ; color: white ; border-color: black ; border-style: outset; border-width: 2px ; padding: 4px}")
        self.close_button.setFont(QtGui.QFont(self.Font,self.fontSize))
        self.close_button.clicked.connect(self.closeEvent)
        self.grid_box.addWidget(self.close_button, 7, 1, 1, 1)
        
        vbox.addLayout(self.grid_box)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

    def submit(self):
        try:
            if int(self.toSort_text.text()) <= 9 and int(self.toSort_text.text()) >= 1:
                self.thread.product = int(self.toSort_text.text())
                self.thread.selectedP = int(self.toSort_text.text())
                self.toSorted.setText(self.thread.productlist.get(self.thread.product))
            else:
                self.toSorted.setText(f"Product Id {self.toSort_text.text()} not between 1 and 9")
        
        except:
            pass


    def closeEvent(self, event):
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Quit")
        fg = self.fg
        des = self.des
        fg.moveCenter(des)
        self.msg.move(fg.center())
        self.msg.setStyleSheet("background-color: #002366")
        self.msg.setText("Are you sure want to Close Application?")
        self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.msg.setStyleSheet("QLabel {background-color: #002366; color: white;}")
        self.msg.setFont(QtGui.QFont(self.Font,12))
        self.msg.setIcon(QMessageBox.Question)
        self.msg.buttonClicked.connect(self.clicked)
        self.msg.exec()
        
    def clicked(self,i):
        if i.text() == "&Yes":
            sys.exit()
        elif i.text() == "&No":
            self.msg.close()



    @pyqtSlot(ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        global detect
        if detect  == True:
            detect = False
            self.detected_name.hide()
            self.detected_name.setText(self.thread.productlist.get(self.thread.product))
            self.detected_name.show()
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__=="__main__":
    #Setting GPIO Pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22,GPIO.OUT) # Signal to PLC (15)

    print("App is intializing")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    a = App()
    print("Launching App.")
    a.show()
    sys.exit(app.exec_())
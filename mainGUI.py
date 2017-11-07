# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainGUI.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StackedWidget(object):
    def setupUi(self, StackedWidget):
        StackedWidget.setObjectName("StackedWidget")
        StackedWidget.resize(400, 300)
        self.page1 = QtWidgets.QWidget()
        self.page1.setObjectName("page1")
        self.startButton = QtWidgets.QPushButton(self.page1)
        self.startButton.setGeometry(QtCore.QRect(130, 180, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.startButton.setFont(font)
        self.startButton.setObjectName("startButton")
        self.titleLabel = QtWidgets.QLabel(self.page1)
        self.titleLabel.setGeometry(QtCore.QRect(100, 60, 211, 51))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.descLabel = QtWidgets.QLabel(self.page1)
        self.descLabel.setGeometry(QtCore.QRect(50, 120, 331, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        font.setItalic(True)
        self.descLabel.setFont(font)
        self.descLabel.setObjectName("descLabel")
        StackedWidget.addWidget(self.page1)
        self.page2 = QtWidgets.QWidget()
        self.page2.setObjectName("page2")
        self.label = QtWidgets.QLabel(self.page2)
        self.label.setGeometry(QtCore.QRect(180, 100, 47, 13))
        self.label.setObjectName("label")
        StackedWidget.addWidget(self.page2)

        self.retranslateUi(StackedWidget)
        StackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(StackedWidget)

    def retranslateUi(self, StackedWidget):
        _translate = QtCore.QCoreApplication.translate
        StackedWidget.setWindowTitle(_translate("StackedWidget", "StackedWidget"))
        self.startButton.setText(_translate("StackedWidget", "Start"))
        self.titleLabel.setText(_translate("StackedWidget", "GAITOR"))
        self.descLabel.setText(_translate("StackedWidget", "Video Analysis of Rats in a Gait Maze"))
        self.label.setText(_translate("StackedWidget", "Page2"))


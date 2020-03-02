# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class ImportURL(QtWidgets.QDialog):
    def __init__(self, parentWindow):
        super().__init__(objectName='importURL')

        self.parentWindow = parentWindow
        self.currentURL = ''

        self.setFixedSize(559, 108)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(self.parentWindow.mainWindow.appIcon)
        self.setWindowTitle('Import text from web')

        parentPos = self.parentWindow.mainWindow.pos()
        parentWidth, parentHeight = self.parentWindow.mainWindow.width(), self.parentWindow.mainWindow.height()
        diffX, diffY = (parentWidth - self.width()) / 2, (parentHeight - self.height()) / 2
        self.move(parentPos.x()+diffX, parentPos.y()+diffY)

        font = QtGui.QFont()
        font.setPointSize(9)

        self.protocolComboBox = QtWidgets.QComboBox(self, objectName='protocolComboBox')
        self.protocolComboBox.setGeometry(QtCore.QRect(10, 20, 65, 22))
        self.protocolComboBox.setFont(font)
        self.protocolComboBox.addItem('https')
        self.protocolComboBox.addItem('http')
        self.protocolComboBox.addItem('ftp')

        self.separatorLabel = QtWidgets.QLabel(self, objectName='separatorLabel')
        self.separatorLabel.setGeometry(QtCore.QRect(83, 20, 21, 20))
        self.separatorLabel.setText('://')
        self.separatorLabel.setFont(font)

        self.urlEdit = QtWidgets.QLineEdit(self, objectName='urlEdit')
        self.urlEdit.setGeometry(QtCore.QRect(107, 20, 441, 21))
        self.urlEdit.setFont(font)

        self.fetchUrlButton = QtWidgets.QPushButton(self, objectName='fetchUrlButton')
        self.fetchUrlButton.setGeometry(QtCore.QRect(217, 63, 125, 35))
        self.fetchUrlButton.setText('Fetch URL')
        self.fetchUrlButton.setEnabled(False)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.urlEdit.textChanged.connect(self.textChanged_urlEdit)
        self.fetchUrlButton.clicked.connect(self.clicked_fetchUrlButton)


    def textChanged_urlEdit(self):
        self.fetchUrlButton.setEnabled(True if self.urlEdit.text() else False)


    def clicked_fetchUrlButton(self):
        self.currentURL = self.protocolComboBox.currentText() + '://' + self.urlEdit.text()
        self.accept()

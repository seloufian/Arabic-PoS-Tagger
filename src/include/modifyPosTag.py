# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class ModifyPosTag(QtWidgets.QDialog):
    def __init__(self, parentWindow, currentTag, listTags):
        super().__init__(objectName='modifyPosTag')

        self.parentWindow = parentWindow
        self.currentTag = currentTag
        self.listTags = listTags
        self.newTag = ''

        self.setFixedSize(280, 170)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(self.parentWindow.mainWindow.appIcon)
        self.setWindowTitle('PoS-Tag Modification')

        parentPos = self.parentWindow.mainWindow.pos()
        parentWidth, parentHeight = self.parentWindow.mainWindow.width(), self.parentWindow.mainWindow.height()
        diffX, diffY = (parentWidth - self.width()) / 2, (parentHeight - self.height()) / 2
        self.move(parentPos.x()+diffX, parentPos.y()+diffY)

        self.currentPosTagLabel = QtWidgets.QLabel(self, objectName='currentPosTagLabel')
        self.currentPosTagLabel.setGeometry(QtCore.QRect(33, 20, 101, 16))
        self.currentPosTagLabel.setText('• Current Pos-Tag :')

        self.newPosTagLabel = QtWidgets.QLabel(self, objectName='newPosTagLabel')
        self.newPosTagLabel.setGeometry(QtCore.QRect(23, 60, 87, 16))
        self.newPosTagLabel.setText('• New Pos-Tag :')

        self.applyButton = QtWidgets.QPushButton(self, objectName='applyButton')
        self.applyButton.setGeometry(QtCore.QRect(94, 120, 91, 35))
        self.applyButton.setText('Apply')

        self.newPosTagComboBox = QtWidgets.QComboBox(self, objectName='newPosTagComboBox')
        self.newPosTagComboBox.setGeometry(QtCore.QRect(111, 59, 147, 22))
        for tag in self.listTags:
            self.newPosTagComboBox.addItem(tag)

        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)

        self.currentPosTagEdit = QtWidgets.QLineEdit(self, objectName='currentPosTagEdit')
        self.currentPosTagEdit.setGeometry(QtCore.QRect(133, 19, 113, 20))
        self.currentPosTagEdit.setFont(font)
        self.currentPosTagEdit.setReadOnly(True)
        self.currentPosTagEdit.setText(self.currentTag)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.applyButton.clicked.connect(self.clicked_applyButton)


    def clicked_applyButton(self):
        self.newTag = self.newPosTagComboBox.currentText()
        self.accept()

# -*- coding: utf-8 -*-
from xml.dom import minidom

from PyQt5 import QtCore, QtWidgets


class ImportQuran(QtWidgets.QDialog):
    def __init__(self, parentWindow):
        super().__init__(objectName='importQuran')

        self.parentWindow = parentWindow

        self.setFixedSize(330, 179)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(self.parentWindow.mainWindow.appIcon)
        self.setWindowTitle('Import text from Quran')

        parentPos = self.parentWindow.mainWindow.pos()
        parentWidth, parentHeight = self.parentWindow.mainWindow.width(), self.parentWindow.mainWindow.height()
        diffX, diffY = (parentWidth - self.width()) / 2, (parentHeight - self.height()) / 2
        self.move(parentPos.x()+diffX, parentPos.y()+diffY)

        self.surahNameLabel = QtWidgets.QLabel(self, objectName='surahNameLabel')
        self.surahNameLabel.setGeometry(QtCore.QRect(34, 20, 91, 16))
        self.surahNameLabel.setText('• surah\'s name :')

        self.surahNameComboBox = QtWidgets.QComboBox(self, objectName='surahNameComboBox')
        self.surahNameComboBox.setGeometry(QtCore.QRect(125, 18, 170, 22))

        quranSourahNames = open(self.parentWindow.mainWindow.appDirectory + 'files/quranSourahNames.txt', encoding='utf-8').readlines()

        counter = 1
        for sourahName in quranSourahNames:
            self.surahNameComboBox.addItem(str(counter) + ' - ' + sourahName.strip())
            counter += 1

        self.startAyaLabel = QtWidgets.QLabel(self, objectName='startAyaLabel')
        self.startAyaLabel.setGeometry(QtCore.QRect(99, 53, 71, 16))
        self.startAyaLabel.setText('• Start Aya :')

        self.endAyaLabel = QtWidgets.QLabel(self, objectName='endAyaLabel')
        self.endAyaLabel.setGeometry(QtCore.QRect(99, 83, 71, 16))
        self.endAyaLabel.setText('• End Aya :')

        self.startAyaSpin = QtWidgets.QSpinBox(self, objectName='startAyaSpin')
        self.startAyaSpin.setGeometry(QtCore.QRect(170, 51, 61, 22))
        self.startAyaSpin.setRange(1, 7)

        self.endAyaSpin = QtWidgets.QSpinBox(self, objectName='endAyaSpin')
        self.endAyaSpin.setGeometry(QtCore.QRect(170, 81, 61, 22))
        self.endAyaSpin.setRange(1, 7)

        self.importTextButton = QtWidgets.QPushButton(self, objectName='importTextButton')
        self.importTextButton.setGeometry(QtCore.QRect(110, 123, 110, 37))
        self.importTextButton.setText('Import text')

        QtCore.QMetaObject.connectSlotsByName(self)

        self.quranXML = minidom.parse(self.parentWindow.mainWindow.appDirectory + 'files/quranText.xml')
        self.currentSurah = self.quranXML.getElementsByTagName('sura')[0]
        self.currentSurahName = self.currentSurah.getAttribute('name')
        self.currentAyas = self.currentSurah.getElementsByTagName('aya')

        self.surahNameComboBox.currentIndexChanged.connect(self.indexChanged_surahNameComboBox)
        self.startAyaSpin.valueChanged.connect(self.valueChanged_ayaSpin)
        self.endAyaSpin.valueChanged.connect(self.valueChanged_ayaSpin)
        self.importTextButton.clicked.connect(self.clicked_importTextButton)


    def indexChanged_surahNameComboBox(self):
        self.currentSurah = self.quranXML.getElementsByTagName('sura')[self.surahNameComboBox.currentIndex()]
        self.currentSurahName = self.currentSurah.getAttribute('name')
        self.currentAyas = self.currentSurah.getElementsByTagName('aya')

        numberAyas = len(self.currentAyas)

        self.startAyaSpin.setMaximum(numberAyas)
        self.startAyaSpin.setValue(1)

        self.endAyaSpin.setMaximum(numberAyas)
        self.endAyaSpin.setValue(numberAyas)


    def valueChanged_ayaSpin(self):
        self.importTextButton.setEnabled(False if self.startAyaSpin.value() > self.endAyaSpin.value() else True)


    def clicked_importTextButton(self):
        selectedAyas = self.currentAyas[self.startAyaSpin.value()-1:self.endAyaSpin.value()]

        self.text = ''

        for aya in selectedAyas:
            self.text += aya.getAttribute('text') + '. '

        self.accept()

# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets

from include.posTagGeneration.posTaggingTab import PosTaggingTab
from include.posTagGeneration.textVisualizationTab import TextVisualizationTab


class PosTagGenerationTab(QtWidgets.QWidget):
    def __init__(self, mainWindow):
        super().__init__(objectName='posTagGenerationTab')

        self.mainWindow = mainWindow

        self.setToolTip('PoS-Tag an input text (automatic mode)')

        self.tabWidget = QtWidgets.QTabWidget(self, objectName='tabWidget')
        self.tabWidget.setGeometry(QtCore.QRect(12, 10, 760, 325))

        self.textVisTab = TextVisualizationTab(self)
        self.tabWidget.addTab(self.textVisTab, 'Text Visualization')

        self.posTagTab = PosTaggingTab(self)
        self.tabWidget.addTab(self.posTagTab, 'PoS Tagging')
        self.tabWidget.setTabEnabled(1, False)

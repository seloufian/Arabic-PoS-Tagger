# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

from include import functions
from include.adminInterface import AdminInterface
from include.posTagInsertionTab import PosTagInsertionTab
from include.posTagModificationTab import PosTagModificationTab
from include.posTagGeneration.posTagGenerationTab import PosTagGenerationTab


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, appDirectory):
        super().__init__()

        self.setObjectName('MainWindow')
        self.setFixedSize(812, 423)
        self.setWindowTitle('Arabic PoS Tagger')

        self.appDirectory = appDirectory
        self.modelCorpus = appDirectory + 'model/corpus/'
        self.modelSources = appDirectory + 'model/sources/'
        self.modelResults = appDirectory + 'model/results/'
        self.modelUpdates = appDirectory + 'model/lexique/'
        self.perLearn = 100
        self.perPh = 100

        self.appIcon = QtGui.QIcon(self.appDirectory + '/files/appIcon.png')
        self.setWindowIcon(self.appIcon)

        self.corpusNames = functions.load_obj('corpusNames', self.modelCorpus)

        self.centralwidget = QtWidgets.QWidget(self, objectName='centralwidget')

        font = QtGui.QFont()
        font.setPointSize(10)

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget, objectName='tabWidget')
        self.tabWidget.setGeometry(QtCore.QRect(12, 10, 788, 370))

        self.posTagInsertionTab = PosTagInsertionTab(self)
        self.tabWidget.addTab(self.posTagInsertionTab, 'PoS-Tag Insertion')

        self.posTagModifTab = PosTagModificationTab(self)
        self.tabWidget.addTab(self.posTagModifTab, 'PoS-Tag Modification')

        self.posTagGenerationTab = PosTagGenerationTab(self)
        self.tabWidget.addTab(self.posTagGenerationTab, 'PoS-Tag Generation')

        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)

        self.statusBarLabel = QtWidgets.QLabel(self.centralwidget, objectName='statusBarLabel')
        self.statusBarLabel.setEnabled(False)
        self.statusBarLabel.setGeometry(QtCore.QRect(5, 380, 781, 20))
        self.statusBarLabel.setFont(font)
        self.statusBarLabel.setText('Welcome to "Arabic PoS Tagger". To start, select an operation..')

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self, objectName='menubar')
        self.menubar.setGeometry(QtCore.QRect(0, 0, 812, 21))

        self.menuAdminInterface = QtWidgets.QAction(self.menubar, objectName='menuAdminInterface')
        self.menuAdminInterface.setText('Admin interface')
        self.menubar.addAction(self.menuAdminInterface)

        self.menuReset = QtWidgets.QAction(self.menubar, objectName='menuReset')
        self.menuReset.setText('Reset')
        self.menubar.addAction(self.menuReset)

        self.setMenuBar(self.menubar)

        self.blurWindow = QtWidgets.QLabel(self.centralwidget, objectName='blurWindow')
        canvas = QtGui.QPixmap(self.size().width(), self.size().height())
        canvas.fill(QtGui.QColor(0, 0, 0, 130))
        self.blurWindow.setPixmap(canvas)
        self.blurWindow.hide()

        QtCore.QMetaObject.connectSlotsByName(self)

        self.menuAdminInterface.triggered.connect(self.triggered_menuAdminInterface)
        self.menuReset.triggered.connect(self.triggered_menuReset)

        self.initUI()


    def initUI(self):
        self.updatedPosLexicon = functions.load_obj('updated_pos_lexicon', self.modelSources)
        self.allTags = []

        for tags in self.updatedPosLexicon.values():
            for tag in tags:
                self.allTags.append(tag)

        self.allTags = set(self.allTags)


    def triggered_menuReset(self, message):
        tempPosTagInsertionTab = self.posTagInsertionTab
        tempPosTagModifTab = self.posTagModifTab
        tempPosTagGenerationTab = self.posTagGenerationTab

        self.tabWidget.removeTab(2)
        self.tabWidget.removeTab(1)
        self.tabWidget.removeTab(0)
        del(tempPosTagInsertionTab)
        del(tempPosTagModifTab)
        del(tempPosTagGenerationTab)

        self.corpusNames = functions.load_obj('corpusNames', self.modelCorpus)
        self.initUI()

        self.posTagInsertionTab = PosTagInsertionTab(self)
        self.tabWidget.addTab(self.posTagInsertionTab, 'PoS-Tag Insertion')

        self.posTagModifTab = PosTagModificationTab(self)
        self.tabWidget.addTab(self.posTagModifTab, 'PoS-Tag Modification')

        self.posTagGenerationTab = PosTagGenerationTab(self)
        self.tabWidget.addTab(self.posTagGenerationTab, 'PoS-Tag Generation')

        self.statusBarLabel.setText(message if isinstance(message, str) else 'Application reseted. To start, select an operation..')


    def triggered_menuAdminInterface(self):
        self.blurWindow.show()

        adminInter = AdminInterface(self)
        accept = adminInter.exec_()

        if accept:
            self.triggered_menuReset(message='Action from "Admin interface" committed successfully.')

        self.blurWindow.hide()

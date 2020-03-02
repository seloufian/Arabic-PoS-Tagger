# -*- coding: utf-8 -*-
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from include import functions


class AdminInterface(QtWidgets.QDialog):
    def __init__(self, mainWindow):
        super().__init__(objectName='adminInterface')

        self.mainWindow = mainWindow

        self.setFixedSize(492, 168)
        self.setWindowTitle('Admin interface')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(self.mainWindow.appIcon)

        parentPos = self.mainWindow.pos()
        parentWidth, parentHeight = self.mainWindow.width(), self.mainWindow.height()
        diffX, diffY = (parentWidth - self.width()) / 2, (parentHeight - self.height()) / 2
        self.move(parentPos.x()+diffX, parentPos.y()+diffY)

        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)

        self.tabWidget = QtWidgets.QTabWidget(self, objectName='tabWidget')
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 471, 139))

        self.newCorpusTab = QtWidgets.QWidget(objectName='newCorpusTab')

        self.corpusPathLabel = QtWidgets.QLabel(self.newCorpusTab, objectName='corpusPathLabel')
        self.corpusPathLabel.setGeometry(QtCore.QRect(14, 19, 81, 21))
        self.corpusPathLabel.setText('• Corpus path :')

        self.corpusPathEdit = QtWidgets.QLineEdit(self.newCorpusTab, objectName='corpusPathEdit')
        self.corpusPathEdit.setGeometry(QtCore.QRect(95, 19, 291, 21))

        self.corpusPathButton = QtWidgets.QPushButton(self.newCorpusTab, objectName='corpusPathButton')
        self.corpusPathButton.setGeometry(QtCore.QRect(385, 18, 71, 23))
        self.corpusPathButton.setText('Browse')

        self.addNewCorpusButton = QtWidgets.QPushButton(self.newCorpusTab, objectName='addNewCorpusButton')
        self.addNewCorpusButton.setGeometry(QtCore.QRect(178, 65, 115, 37))
        self.addNewCorpusButton.setText('Add new corpus')
        self.addNewCorpusButton.setEnabled(False)

        self.tabWidget.addTab(self.newCorpusTab, 'Add new corpus')

        self.deleteCorpusTab = QtWidgets.QWidget(objectName='deleteCorpusTab')

        self.selectCorpusComboBox = QtWidgets.QComboBox(self.deleteCorpusTab, objectName='selectCorpusComboBox')
        self.selectCorpusComboBox.setGeometry(QtCore.QRect(173, 20, 212, 21))

        self.deleteCorpusButton = QtWidgets.QPushButton(self.deleteCorpusTab, objectName='deleteCorpusButton')
        self.deleteCorpusButton.setGeometry(QtCore.QRect(178, 65, 115, 37))
        self.deleteCorpusButton.setText('Delete corpus')

        self.selectCorpusLabel = QtWidgets.QLabel(self.deleteCorpusTab, objectName='selectCorpusLabel')
        self.selectCorpusLabel.setGeometry(QtCore.QRect(86, 19, 87, 21))
        self.selectCorpusLabel.setText('• Corpus name :')

        self.tabWidget.addTab(self.deleteCorpusTab, 'Delete a corpus')

        self.statusBarLabel = QtWidgets.QLabel(self, objectName='statusBarLabel')
        self.statusBarLabel.setEnabled(False)
        self.statusBarLabel.setGeometry(QtCore.QRect(5, 150, 461, 16))
        self.statusBarLabel.setFont(font)
        self.statusBarLabel.setText('Welcome to "Admin interface". Add/delete a corpus..')

        QtCore.QMetaObject.connectSlotsByName(self)

        self.initUI()


    def initUI(self):
        for name in self.mainWindow.corpusNames:
            self.selectCorpusComboBox.addItem(name)

        self.corpusPathButton.clicked.connect(self.clicked_corpusPathButton)
        self.addNewCorpusButton.clicked.connect(self.clicked_addNewCorpusButton)
        self.deleteCorpusButton.clicked.connect(self.clicked_deleteCorpusButton)


    def clicked_corpusPathButton(self):
        indexFilePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Browse a corpus file', self.mainWindow.appDirectory, filter="xml file (*.xml)")[0]

        if indexFilePath:
            self.corpusPathEdit.setText(indexFilePath.replace('\\', '/'))
            self.addNewCorpusButton.setEnabled(True)


    def clicked_addNewCorpusButton(self):
        questionMsg = 'Are you sure you want to add a new corpus ?'
        yes, no = QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
        reply = QtWidgets.QMessageBox.question(self, 'Add new corpus', questionMsg, yes, no)

        if reply == yes:
            addCorpusPath = self.corpusPathEdit.text()
            addCorpusName = addCorpusPath.split('/')[-1]

            addCorpusFile = open(self.corpusPathEdit.text(), encoding='utf-8').read()
            saveCorpusFile = open(self.mainWindow.appDirectory + 'model/corpus/' + addCorpusName, 'w', encoding='utf-8')
            saveCorpusFile.write(addCorpusFile)
            saveCorpusFile.close()

            corpusNames = functions.load_obj('corpusNames', self.mainWindow.appDirectory + 'model/corpus/')
            corpusNames.append(addCorpusName[:-4]) # Remove the extension
            functions.save_obj(corpusNames, 'corpusNames', self.mainWindow.appDirectory + 'model/corpus/')

            annotated_corpus_path = self.mainWindow.appDirectory + 'model/corpus/'
            path_sources = self.mainWindow.appDirectory + 'model/sources/'
            functions.generate_model(annotated_corpus_path, corpusNames, path_sources, self.mainWindow.modelUpdates, annotated_corpus_dictionnaries_updated = False, learning_percentage = self.mainWindow.perLearn, percent_phrases = self.mainWindow.perPh)

            self.accept()


    def clicked_deleteCorpusButton(self):
        questionMsg = 'Are you sure you want to delete selected corpus ?'
        yes, no = QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
        reply = QtWidgets.QMessageBox.question(self, 'Add new corpus', questionMsg, yes, no)

        if reply == yes:
            selectedCorpus = self.selectCorpusComboBox.currentText()

            deleteCorpus = self.mainWindow.appDirectory + 'model/corpus/' + selectedCorpus + '.xml'
            os.remove(deleteCorpus)

            corpusNames = functions.load_obj('corpusNames', self.mainWindow.appDirectory + 'model/corpus/')
            corpusNames.remove(selectedCorpus)
            functions.save_obj(corpusNames, 'corpusNames', self.mainWindow.appDirectory + 'model/corpus/')

            os.remove(self.mainWindow.appDirectory + 'model/sources/talaa_pos_dic_phrase_' + selectedCorpus + '.pkl')

            annotated_corpus_path = self.mainWindow.appDirectory + 'model/corpus/'
            path_sources = self.mainWindow.appDirectory + 'model/sources/'

            functions.generate_model(annotated_corpus_path, corpusNames, path_sources, self.mainWindow.modelUpdates, annotated_corpus_dictionnaries_updated = False, learning_percentage = self.mainWindow.perLearn, percent_phrases = self.mainWindow.perPh)

            self.accept()

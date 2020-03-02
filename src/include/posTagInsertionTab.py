# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

from include import functions


class PosTagInsertionTab(QtWidgets.QWidget):
    def __init__(self, mainWindow):
        super().__init__(objectName='posTagInsertionTab')

        self.mainWindow = mainWindow

        self.setToolTip('Insert a tegged text into a corpus (manual mode)')

        font = QtGui.QFont()
        font.setPointSize(10)

        self.rawTextGroup = QtWidgets.QGroupBox(self, objectName='rawTextGroup')
        self.rawTextGroup.setGeometry(QtCore.QRect(10, 10, 374, 251))
        self.rawTextGroup.setCheckable(True)
        self.rawTextGroup.setChecked(False)
        self.rawTextGroup.setTitle('Raw text insertion')

        self.rawTextImportButton = QtWidgets.QPushButton(self.rawTextGroup, objectName='rawTextImportButton')
        self.rawTextImportButton.setGeometry(QtCore.QRect(122, 204, 131, 35))
        self.rawTextImportButton.setText('Import text from file')

        self.rawTextEdit = QtWidgets.QTextEdit(self.rawTextGroup, objectName='rawTextEdit')
        self.rawTextEdit.setGeometry(QtCore.QRect(12, 20, 351, 171))
        self.rawTextEdit.setFont(font)

        self.taggedTextGroup = QtWidgets.QGroupBox(self, objectName='taggedTextGroup')
        self.taggedTextGroup.setGeometry(QtCore.QRect(399, 10, 374, 251))
        self.taggedTextGroup.setTitle('Tagged text insertion')

        self.taggedTextImportButton = QtWidgets.QPushButton(self.taggedTextGroup, objectName='taggedTextImportButton')
        self.taggedTextImportButton.setGeometry(QtCore.QRect(102, 204, 171, 35))
        self.taggedTextImportButton.setText('Import tagged text from file')

        self.taggedTextEdit = QtWidgets.QTextEdit(self.taggedTextGroup, objectName='taggedTextEdit')
        self.taggedTextEdit.setGeometry(QtCore.QRect(12, 20, 351, 171))
        self.taggedTextEdit.setFont(font)

        self.addTextButton = QtWidgets.QPushButton(self, objectName='addTextButton')
        self.addTextButton.setGeometry(QtCore.QRect(516, 291, 111, 41))
        self.addTextButton.setText('Add text')
        self.addTextButton.setEnabled(False)

        self.corpusNameLabel = QtWidgets.QLabel(self, objectName='corpusNameLabel')
        self.corpusNameLabel.setGeometry(QtCore.QRect(186, 303, 101, 16))
        self.corpusNameLabel.setText('• Select a corpus :')

        self.corpusNameComboBox = QtWidgets.QComboBox(self, objectName='corpusNameComboBox')
        self.corpusNameComboBox.setGeometry(QtCore.QRect(291, 300, 200, 22))

        self.initUI()


    def initUI(self):
        for name in self.mainWindow.corpusNames:
            self.corpusNameComboBox.addItem(name)

        self.rawTextImportButton.clicked.connect(self.clicked_rawTextImportButton)
        self.taggedTextImportButton.clicked.connect(self.clicked_taggedTextImportButton)

        self.taggedTextEdit.textChanged.connect(self.textChanged_taggedTextEdit)

        self.addTextButton.clicked.connect(self.clicked_addTextButton)


    def clicked_rawTextImportButton(self):
        self.mainWindow.blurWindow.show()

        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Import a raw text file', self.mainWindow.appDirectory, filter="Text file (*.txt)")[0]

        if filePath:
            self.mainWindow.statusBarLabel.setText('Raw text file from  "' + filePath + '"  imported')
            text = open(filePath, encoding='utf-8').read()
            self.rawTextEdit.setPlainText(text)

        self.mainWindow.blurWindow.hide()


    def clicked_taggedTextImportButton(self):
        self.mainWindow.blurWindow.show()

        filePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Import a tagged text file', self.mainWindow.appDirectory, filter="Text file (*.txt)")[0]

        if filePath:
            self.mainWindow.statusBarLabel.setText('tagged text file from  "' + filePath + '"  imported')
            textList = open(filePath, encoding='utf-8').read().split()

            text = ''
            try:
                for word in textList:
                    tokenTag = word.split('/')
                    text += tokenTag[0] + '/' + '<span style="background-color: yellow; font: bold 11px;">' + tokenTag[1] + '</span> '
            except:
                self.mainWindow.statusBarLabel.setText('tagged text file  "' + filePath + '"  contains some errors.')

            self.taggedTextEdit.setHtml(text)

        self.mainWindow.blurWindow.hide()


    def textChanged_taggedTextEdit(self):
        self.addTextButton.setEnabled(True if self.taggedTextEdit.toPlainText().strip() else False)


    def clicked_addTextButton(self):
        inputText = self.rawTextEdit.toPlainText() if self.rawTextGroup.isChecked() else '...'

        taggedTextList = self.taggedTextEdit.toPlainText().split()
        stemList = []
        tagList = ['NULL']

        try:
            for stemTag in taggedTextList:
                parts = stemTag.split('/')
                stemList.append(parts[0])
                tagList.append(parts[1])

            selectedCorpus = self.corpusNameComboBox.currentText()

            functions.add_new_sent(inputText, stemList, tagList, self.mainWindow.modelCorpus, selectedCorpus, self.mainWindow.modelSources)
            functions.generate_model(self.mainWindow.modelCorpus, self.mainWindow.corpusNames, self.mainWindow.modelSources, self.mainWindow.modelUpdates, annotated_corpus_dictionnaries_updated = False, learning_percentage = self.mainWindow.perLearn, percent_phrases = self.mainWindow.perPh)

            self.mainWindow.triggered_menuReset(message='Sentence added successfully to corpus : "' + selectedCorpus + '" (in last position).')

        except:
            self.mainWindow.statusBarLabel.setText('tagged text contains some errors.')

# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

from include import functions
from include.modifyPosTag import ModifyPosTag


class PosTagModificationTab(QtWidgets.QWidget):
    def __init__(self, mainWindow):
        super().__init__(objectName='posTagModifTab')

        self.mainWindow = mainWindow

        self.setToolTip('Modify PoS-Tags of sentence in a corpus (manual mode)')

        font = QtGui.QFont()
        font.setPointSize(10)

        self.corpusNameLabel = QtWidgets.QLabel(self, objectName='corpusNameLabel')
        self.corpusNameLabel.setGeometry(QtCore.QRect(193, 20, 91, 16))
        self.corpusNameLabel.setText('• Corpus name :')

        self.sentenceNumberLabel = QtWidgets.QLabel(self, objectName='sentenceNumberLabel')
        self.sentenceNumberLabel.setGeometry(QtCore.QRect(233, 50, 111, 16))
        self.sentenceNumberLabel.setText('• Sentence number :')

        self.corpusNameComboBox = QtWidgets.QComboBox(self, objectName='corpusNameComboBox')
        self.corpusNameComboBox.setGeometry(QtCore.QRect(283, 20, 200, 22))

        self.sentenceNumberSpin = QtWidgets.QSpinBox(self, objectName='sentenceNumberSpin')
        self.sentenceNumberSpin.setGeometry(QtCore.QRect(343, 50, 111, 22))
        self.sentenceNumberSpin.setPrefix('Sentence   ')

        self.modifEdit = QtWidgets.QTextEdit(self, objectName='modifEdit')
        self.modifEdit.setGeometry(QtCore.QRect(10, 90, 760, 180))
        self.modifEdit.setFont(font)

        self.submitModifButton = QtWidgets.QPushButton(self, objectName='submitModifButton')
        self.submitModifButton.setGeometry(QtCore.QRect(323, 287, 141, 41))
        self.submitModifButton.setText('Submit modifications')

        self.selectButton = QtWidgets.QPushButton(self, objectName='selectButton')
        self.selectButton.setGeometry(QtCore.QRect(500, 23, 111, 41))
        self.selectButton.setText('Select sentence')

        self.initUi()


    def initUi(self):
        for name in self.mainWindow.corpusNames:
            self.corpusNameComboBox.addItem(name)

        currentCorpus = self.corpusNameComboBox.currentText()
        self.currentCorpus = functions.load_obj('talaa_pos_dic_phrase_'+currentCorpus, self.mainWindow.modelSources)
        self.sentenceNumberSpin.setRange(1, len(self.currentCorpus))

        self.corpusNameComboBox.currentIndexChanged.connect(self.changed_corpusNameComboBox)
        self.selectButton.clicked.connect(self.clicked_selectButton)
        self.submitModifButton.clicked.connect(self.clicked_submitModifButton)

        self.modifEdit.selectionChanged.connect(self.selectionChanged_taggedTextEdit)
        self.sentenceNumberSpin.valueChanged.connect(self.valueChanged_sentenceNumberSpin)

        self.submitModifButton.setEnabled(False)

        self.modifEdit.setReadOnly(True)
        self.modifEdit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.modifEdit.menu = QtWidgets.QMenu(self)
        modifyTagAction = QtWidgets.QAction('Modify tag', self)
        modifyTagAction.triggered.connect(self.triggered_modifyTagAction)
        self.modifEdit.menu.addAction(modifyTagAction)


    def changed_corpusNameComboBox(self):
        self.submitModifButton.setEnabled(False)
        self.modifEdit.setText('')

        currentCorpus = self.corpusNameComboBox.currentText()
        self.currentCorpus = functions.load_obj('talaa_pos_dic_phrase_'+currentCorpus, self.mainWindow.modelSources)
        self.sentenceNumberSpin.setRange(1, len(self.currentCorpus))
        self.sentenceNumberSpin.setValue(1)


    def valueChanged_sentenceNumberSpin(self):
        self.submitModifButton.setEnabled(False)
        self.modifEdit.setText('')


    def clicked_selectButton(self):
        self.submitModifButton.setEnabled(False)

        selectedSentence = self.currentCorpus[self.sentenceNumberSpin.value()-1]

        text = ''
        for i in range(0, len(selectedSentence[1])):
            text += selectedSentence[1][i] + '/' + '<span style="background-color: yellow; font: bold 11px;">' + selectedSentence[2][i+1] + '</span>' + '\n'

        self.modifEdit.setText(text)


    def clicked_submitModifButton(self):
        text = self.modifEdit.toPlainText().split()

        token_tag = []
        for word in text:
            token_tag.append(word.split('/'))

        phraseNum = self.sentenceNumberSpin.value()-1
        selectedCorpus = self.corpusNameComboBox.currentText()

        functions.edit_annotated_corpus(phraseNum, token_tag, self.mainWindow.modelCorpus, selectedCorpus, self.mainWindow.modelSources)
        functions.generate_model(self.mainWindow.modelCorpus, self.mainWindow.corpusNames, self.mainWindow.modelSources, self.mainWindow.modelUpdates, annotated_corpus_dictionnaries_updated = False, learning_percentage = self.mainWindow.perLearn, percent_phrases = self.mainWindow.perPh)

        self.changed_corpusNameComboBox()

        self.mainWindow.statusBarLabel.setText('Sentence "' + str(phraseNum+1) + '" from "' + selectedCorpus + '" updated successfully.')


    def selectionChanged_taggedTextEdit(self):
        cursor = self.modifEdit.textCursor()

        selectedText = cursor.selectedText()

        if selectedText in self.mainWindow.allTags:
            cursorRelativePos = self.modifEdit.cursorRect()
            point = QtCore.QPoint(cursorRelativePos.x()-10, cursorRelativePos.y()+20)
            cursorGlobalPos = self.modifEdit.mapToGlobal(point)
            self.modifEdit.menu.move(cursorGlobalPos)
            self.modifEdit.menu.show()


    def triggered_modifyTagAction(self):
        cursor = self.modifEdit.textCursor()
        selectedText = cursor.selectedText()

        self.mainWindow.blurWindow.show()

        modPosTag = ModifyPosTag(self, selectedText, self.mainWindow.allTags)
        accept = modPosTag.exec_()

        if accept and modPosTag.newTag != selectedText:
            cursor.insertText(modPosTag.newTag)
            self.submitModifButton.setEnabled(True)

        self.mainWindow.blurWindow.hide()

# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

from include import functions
from include.modifyPosTag import ModifyPosTag


class PosTaggingTab(QtWidgets.QWidget):
    def __init__(self, parentWindow):
        super().__init__(objectName='posTagTab')

        self.parentWindow = parentWindow
        self.mainWindow = self.parentWindow.mainWindow

        font = QtGui.QFont()
        font.setPointSize(10)

        self.outputTextGroup = QtWidgets.QGroupBox(self, objectName='outputTextGroup')
        self.outputTextGroup.setGeometry(QtCore.QRect(15, 10, 505, 280))
        self.outputTextGroup.setTitle('Output text')

        self.taggedTextEdit = QtWidgets.QTextEdit(self.outputTextGroup, objectName='taggedTextEdit')
        self.taggedTextEdit.setGeometry(QtCore.QRect(10, 20, 485, 200))
        self.taggedTextEdit.setFont(font)
        self.taggedTextEdit.setReadOnly(True)

        self.corpusNameLabel = QtWidgets.QLabel(self.outputTextGroup, objectName='corpusNameLabel')
        self.corpusNameLabel.setGeometry(QtCore.QRect(12, 238, 106, 16))
        self.corpusNameLabel.setText('• Select a corpus :')

        self.corpusNameComboBox = QtWidgets.QComboBox(self.outputTextGroup, objectName='corpusNameComboBox')
        self.corpusNameComboBox.setGeometry(QtCore.QRect(118, 237, 200, 22))
        self.corpusNameComboBox.setEnabled(False)
        for name in self.mainWindow.corpusNames:
            self.corpusNameComboBox.addItem(name)

        self.submitModifButton = QtWidgets.QPushButton(self.outputTextGroup, objectName='submitModifButton')
        self.submitModifButton.setGeometry(QtCore.QRect(355, 229, 141, 41))
        self.submitModifButton.setEnabled(False)
        self.submitModifButton.setText('Submit modifications')

        self.outStatsGroup = QtWidgets.QGroupBox(self, objectName='outStatsGroup')
        self.outStatsGroup.setGeometry(QtCore.QRect(528, 13, 211, 131))
        self.outStatsGroup.setTitle('Statistics')

        font.setBold(True)

        self.numStemLabel = QtWidgets.QLabel(self.outStatsGroup, objectName='numStemLabel')
        self.numStemLabel.setGeometry(QtCore.QRect(10, 25, 100, 16))
        self.numStemLabel.setText('• Stem count :')

        self.numStemEdit = QtWidgets.QLineEdit(self.outStatsGroup, objectName='numStemEdit')
        self.numStemEdit.setGeometry(QtCore.QRect(110, 25, 91, 21))
        self.numStemEdit.setFont(font)
        self.numStemEdit.setReadOnly(True)

        self.numUnkTagsLabel = QtWidgets.QLabel(self.outStatsGroup, objectName='numUnkTagsLabel')
        self.numUnkTagsLabel.setGeometry(QtCore.QRect(10, 58, 121, 16))
        self.numUnkTagsLabel.setText('• Uknown stem count :')

        self.numUnkTagsEdit = QtWidgets.QLineEdit(self.outStatsGroup, objectName='numUnkTagsEdit')
        self.numUnkTagsEdit.setGeometry(QtCore.QRect(130, 58, 71, 21))
        self.numUnkTagsEdit.setFont(font)
        self.numUnkTagsEdit.setReadOnly(True)

        self.mostFreqTagLabel = QtWidgets.QLabel(self.outStatsGroup, objectName='mostFreqTagLabel')
        self.mostFreqTagLabel.setGeometry(QtCore.QRect(10, 90, 135, 16))
        self.mostFreqTagLabel.setText('• Most frequent PoS-Tag :')

        self.mostFreqTagEdit = QtWidgets.QLineEdit(self.outStatsGroup, objectName='mostFreqTagEdit')
        self.mostFreqTagEdit.setGeometry(QtCore.QRect(144, 90, 57, 21))
        self.mostFreqTagEdit.setFont(font)
        self.mostFreqTagEdit.setReadOnly(True)

        self.searchStemGroup = QtWidgets.QGroupBox(self, objectName='searchStemGroup')
        self.searchStemGroup.setGeometry(QtCore.QRect(528, 153, 211, 131))
        self.searchStemGroup.setTitle('Search stems')

        self.searchStemButton = QtWidgets.QPushButton(self.searchStemGroup, objectName='searchStemButton')
        self.searchStemButton.setGeometry(QtCore.QRect(60, 80, 91, 37))
        self.searchStemButton.setText('Search stem')
        self.searchStemButton.setEnabled(False)

        self.searchStemEdit = QtWidgets.QLineEdit(self.searchStemGroup, objectName='searchStemEdit')
        self.searchStemEdit.setGeometry(QtCore.QRect(20, 30, 171, 31))
        self.searchStemEdit.setFont(font)

        self.taggedTextEdit.selectionChanged.connect(self.selectionChanged_taggedTextEdit)
        self.submitModifButton.clicked.connect(self.clicked_submitModifButton)

        self.searchStemEdit.textChanged.connect(self.textChanged_searchStemEdit)
        self.searchStemButton.clicked.connect(self.clicked_searchStemButton)

        self.taggedTextEdit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.taggedTextEdit.menu = QtWidgets.QMenu(self)
        modifyTagAction = QtWidgets.QAction('Modify tag', self)
        modifyTagAction.triggered.connect(self.triggered_modifyTagAction)
        self.taggedTextEdit.menu.addAction(modifyTagAction)


    def textChanged_searchStemEdit(self):
        self.searchStemButton.setEnabled(True if self.searchStemEdit.text().strip() else False)


    def clicked_searchStemButton(self):
        searchStem = self.searchStemEdit.text().strip()

        textList = self.taggedTextEdit.toPlainText().split()
        numMatches = 0
        text = ''

        for word in textList:
            tokTag = word.split('/')
            tokTag[1] = '<span style="background-color: yellow; font: bold 11px;">' + tokTag[1] + '</span>'

            if tokTag[0] == searchStem:
                numMatches += 1
                tokTag[0] = '<span style="background-color: aqua;">' + tokTag[0] + '</span>'

            text += tokTag[0] + '/' + tokTag[1] + ' '

        self.taggedTextEdit.setHtml(text.strip())
        self.mainWindow.statusBarLabel.setText('Number of matches of stem  "' + searchStem + '"  is :  ' + str(numMatches))


    def selectionChanged_taggedTextEdit(self):
        cursor = self.taggedTextEdit.textCursor()

        selectedText = cursor.selectedText()

        if selectedText in self.mainWindow.allTags:
            cursorRelativePos = self.taggedTextEdit.cursorRect()
            point = QtCore.QPoint(cursorRelativePos.x()-10, cursorRelativePos.y()+20)
            cursorGlobalPos = self.taggedTextEdit.mapToGlobal(point)
            self.taggedTextEdit.menu.move(cursorGlobalPos)
            self.taggedTextEdit.menu.show()


    def triggered_modifyTagAction(self):
        cursor = self.taggedTextEdit.textCursor()
        selectedText = cursor.selectedText()

        self.mainWindow.blurWindow.show()

        modPosTag = ModifyPosTag(self, selectedText, self.mainWindow.allTags)
        accept = modPosTag.exec_()

        if accept and modPosTag.newTag != selectedText:
            cursor.insertText(modPosTag.newTag)
            self.corpusNameComboBox.setEnabled(True)
            self.submitModifButton.setEnabled(True)

        self.mainWindow.blurWindow.hide()


    def clicked_submitModifButton(self):
        inputText = self.parentWindow.textVisTab.inputText

        taggedTextList = self.taggedTextEdit.toPlainText().split()
        stemList = []
        tagList = ['NULL']

        for stemTag in taggedTextList:
            parts = stemTag.split('/')
            stemList.append(parts[0])
            tagList.append(parts[1])

        selectedCorpus = self.corpusNameComboBox.currentText()

        functions.add_new_sent(inputText, stemList, tagList, self.mainWindow.modelCorpus, selectedCorpus, self.mainWindow.modelSources)
        functions.generate_model(self.mainWindow.modelCorpus, self.mainWindow.corpusNames, self.mainWindow.modelSources, self.mainWindow.modelUpdates, annotated_corpus_dictionnaries_updated = False, learning_percentage = self.mainWindow.perLearn, percent_phrases = self.mainWindow.perPh)

        self.mainWindow.triggered_menuReset(message='Sentence added successfully to corpus : "' + selectedCorpus + '" (in last position).')

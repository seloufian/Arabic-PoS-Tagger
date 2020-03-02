# -*- coding: utf-8 -*-
import re
import unicodedata as ud

from bs4 import BeautifulSoup
from nltk import FreqDist
from PyQt5 import QtCore, QtGui, QtWidgets
from urllib.request import urlopen

from include import functions
from include.posTagGeneration.importURL import ImportURL
from include.posTagGeneration.importQuran import ImportQuran


class TextVisualizationTab(QtWidgets.QWidget):
    def __init__(self, parentWindow):
        super().__init__(objectName='textVisTab')

        self.parentWindow = parentWindow
        self.mainWindow = self.parentWindow.mainWindow

        font = QtGui.QFont()
        font.setPointSize(10)

        self.inputTextGroup = QtWidgets.QGroupBox(self, objectName='inputTextGroup')
        self.inputTextGroup.setGeometry(QtCore.QRect(15, 10, 505, 280))
        self.inputTextGroup.setTitle('Input text')

        self.inputTextEdit = QtWidgets.QTextEdit(self.inputTextGroup, objectName='inputTextEdit')
        self.inputTextEdit.setGeometry(QtCore.QRect(10, 20, 485, 200))
        self.inputTextEdit.setFont(font)

        self.importFileButton = QtWidgets.QPushButton(self.inputTextGroup, objectName='importFileButton')
        self.importFileButton.setGeometry(QtCore.QRect(10, 229, 135, 41))
        self.importFileButton.setText('Import from file')

        self.importWebButton = QtWidgets.QPushButton(self.inputTextGroup, objectName='importWebButton')
        self.importWebButton.setGeometry(QtCore.QRect(185, 229, 135, 41))
        self.importWebButton.setText('Import from web')

        self.importQuranButton = QtWidgets.QPushButton(self.inputTextGroup, objectName='importQuranButton')
        self.importQuranButton.setGeometry(QtCore.QRect(361, 229, 135, 41))
        self.importQuranButton.setText('Quran versets')

        self.startPosTagButton = QtWidgets.QPushButton(self, objectName='startPosTagButton')
        self.startPosTagButton.setGeometry(QtCore.QRect(580, 253, 121, 41))
        self.startPosTagButton.setText('Start Pos-Tagging')
        self.startPosTagButton.setEnabled(False)

        self.inStatsGroup = QtWidgets.QGroupBox(self, objectName='inStatsGroup')
        self.inStatsGroup.setGeometry(QtCore.QRect(528, 10, 211, 115))
        self.inStatsGroup.setTitle('Statistics')
        self.inStatsGroup.setEnabled(False)

        font.setBold(True)

        self.numWordEdit = QtWidgets.QLineEdit(self.inStatsGroup, objectName='numWordEdit')
        self.numWordEdit.setGeometry(QtCore.QRect(110, 20, 91, 21))
        self.numWordEdit.setFont(font)
        self.numWordEdit.setReadOnly(True)

        self.numWordLabel = QtWidgets.QLabel(self.inStatsGroup, objectName='numWordLabel')
        self.numWordLabel.setGeometry(QtCore.QRect(10, 20, 101, 16))
        self.numWordLabel.setText('• Word count :')

        self.numSenteceLabel = QtWidgets.QLabel(self.inStatsGroup, objectName='numSenteceLabel')
        self.numSenteceLabel.setGeometry(QtCore.QRect(10, 53, 111, 16))
        self.numSenteceLabel.setText('• Sentence count :')

        self.mostFreqWordLabel = QtWidgets.QLabel(self.inStatsGroup, objectName='mostFreqWordLabel')
        self.mostFreqWordLabel.setGeometry(QtCore.QRect(10, 83, 121, 16))
        self.mostFreqWordLabel.setText('• Most frequent word :')

        self.numSentenceEdit = QtWidgets.QLineEdit(self.inStatsGroup, objectName='numSentenceEdit')
        self.numSentenceEdit.setGeometry(QtCore.QRect(120, 53, 81, 21))
        self.numSentenceEdit.setFont(font)
        self.numSentenceEdit.setReadOnly(True)

        self.mostFreqWordEdit = QtWidgets.QLineEdit(self.inStatsGroup, objectName='mostFreqWordEdit')
        self.mostFreqWordEdit.setGeometry(QtCore.QRect(130, 83, 71, 21))
        self.mostFreqWordEdit.setFont(font)
        self.mostFreqWordEdit.setReadOnly(True)

        self.searchWordGroup = QtWidgets.QGroupBox(self, objectName='searchWordGroup')
        self.searchWordGroup.setGeometry(QtCore.QRect(528, 135, 211, 110))
        self.searchWordGroup.setTitle('Search word/expression')
        self.searchWordGroup.setEnabled(False)

        self.searchWordEdit = QtWidgets.QLineEdit(self.searchWordGroup, objectName='searchWordEdit')
        self.searchWordEdit.setGeometry(QtCore.QRect(20, 20, 171, 31))

        self.searchWordButton = QtWidgets.QPushButton(self.searchWordGroup, objectName='searchWordButton')
        self.searchWordButton.setGeometry(QtCore.QRect(38, 60, 136, 37))
        self.searchWordButton.setText('Search word/expression')
        self.searchWordButton.setEnabled(False)


        self.importFileButton.clicked.connect(self.clicked_importFileButton)
        self.importWebButton.clicked.connect(self.clicked_importWebButton)
        self.importQuranButton.clicked.connect(self.clicked_importQuranButton)

        self.inputTextEdit.textChanged.connect(self.textChanged_inputTextEdit)

        self.searchWordEdit.textChanged.connect(self.textChanged_searchWordEdit)
        self.searchWordButton.clicked.connect(self.clicked_searchWordButton)

        self.startPosTagButton.clicked.connect(self.clicked_startPosTagButton)


    def clicked_importFileButton(self):
        self.mainWindow.blurWindow.show()

        indexFilePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Import a text file', self.mainWindow.appDirectory, filter="Text file (*.txt)")[0]

        if indexFilePath:
            self.mainWindow.statusBarLabel.setText('Text file from  "' + indexFilePath + '"  imported')
            text = open(indexFilePath, encoding='utf-8').read()
            self.inputTextEdit.setPlainText(text)

        self.mainWindow.blurWindow.hide()


    def clicked_importWebButton(self):
        self.mainWindow.blurWindow.show()

        imURL = ImportURL(self.parentWindow)
        accept = imURL.exec_()

        if accept:
            page = imURL.currentURL
            self.mainWindow.statusBarLabel.setText('Text file from  "' + page + '"  imported')

            page = BeautifulSoup(urlopen(page), 'lxml')

            page = page.get_text()
            page = re.sub('&nbsp', ' ', page)
            page = re.sub('\s+', ' ', page)

            self.inputTextEdit.setPlainText(page)

        self.mainWindow.blurWindow.hide()


    def clicked_importQuranButton(self):
        self.mainWindow.blurWindow.show()

        imQuran = ImportQuran(self.parentWindow)
        accept = imQuran.exec_()

        if accept:
            beginAya = str(imQuran.startAyaSpin.value())
            endAya = str(imQuran.endAyaSpin.value())
            self.mainWindow.statusBarLabel.setText('Ayas from ' + beginAya + ' to ' + endAya + ' of  "سورة ' + imQuran.currentSurahName + '"  imported')
            self.inputTextEdit.setPlainText(imQuran.text)

        self.mainWindow.blurWindow.hide()


    def textChanged_inputTextEdit(self):
        inputText = self.inputTextEdit.toPlainText().strip()
        inputText = ''.join(c for c in inputText if not ud.category(c).startswith('P')) # Delete all ponctuations (Arabic included)

        inputTokens = functions.tokenization(inputText)
        freqDist = FreqDist(inputTokens)

        self.numWordEdit.setText(str(freqDist.N()))
        self.mostFreqWordEdit.setText(freqDist.max())

        numSentences = len(functions.tok_stem(self.inputTextEdit.toPlainText(), False))
        self.numSentenceEdit.setText(str(numSentences))

        self.inStatsGroup.setEnabled(True if self.inputTextEdit.toPlainText().strip() else False)
        self.searchWordGroup.setEnabled(True if self.inputTextEdit.toPlainText().strip() else False)
        self.startPosTagButton.setEnabled(True if self.inputTextEdit.toPlainText().strip() else False)


    def textChanged_searchWordEdit(self):
        self.searchWordButton.setEnabled(True if self.searchWordEdit.text().strip() else False)


    def clicked_searchWordButton(self):
        searchText = re.escape(self.searchWordEdit.text())
        resultText = re.sub('('+searchText+')', '<span style="background-color: aqua;">\\1</span>', self.inputTextEdit.toPlainText())
        self.inputTextEdit.setHtml(resultText)

        numberMatches = len(re.findall(searchText, self.inputTextEdit.toPlainText()))
        self.mainWindow.statusBarLabel.setText('Number of matches of word/expression  "'+ searchText.replace('\\', '') + '"  is :  '+str(numberMatches))


    def clicked_startPosTagButton(self):
        self.inputText = self.inputTextEdit.toPlainText()

        file = open(self.mainWindow.modelResults+'Input.txt', 'w', encoding='utf-8')
        file.write(self.inputText)
        file.close()

        tokStems = functions.tok_stem(self.inputTextEdit.toPlainText())
        normTokStems = functions.normalization(tokStems, self.mainWindow.modelSources)

        numberStems = len(normTokStems)
        numberUNK = 0

        text = ''
        counter = 0
        while counter < len(tokStems):
            text += tokStems[counter] + ' '
            if normTokStems[counter] == 'مجه':
                numberUNK += 1
            counter += 1

        file = open(self.mainWindow.modelResults+'Affix.txt', 'w', encoding='utf-8')
        file.write(text)
        file.close()

        stemsTags = functions.viterbi(normTokStems, self.mainWindow.modelSources)

        text = ''
        tagsText = ''
        counter = 0
        while counter < len(stemsTags):
            tag = stemsTags[counter]
            token = tokStems[counter]

            tagsText += tag + ' '
            text += token + '/' + '<span style="background-color: yellow; font: bold 11px;">' + tag + '</span>' + ' '

            counter += 1

        file = open(self.mainWindow.modelResults+'Tag.txt', 'w', encoding='utf-8')
        file.write(tagsText)
        file.close()

        self.parentWindow.posTagTab.taggedTextEdit.setHtml(text)

        file = open(self.mainWindow.modelResults+'Out.txt', 'w', encoding='utf-8')
        file.write(self.parentWindow.posTagTab.taggedTextEdit.toPlainText())
        file.close()

        self.parentWindow.posTagTab.numStemEdit.setText(str(numberStems))
        self.parentWindow.posTagTab.numUnkTagsEdit.setText(str(numberUNK))

        tagsList = tagsText.split()
        freqDist = FreqDist(tagsList)
        self.parentWindow.posTagTab.mostFreqTagEdit.setText(freqDist.max())

        self.mainWindow.statusBarLabel.setText('Input text has been PoS-Tagged. Check text files in  "/model/results/"')

        self.parentWindow.tabWidget.setTabEnabled(1, True)

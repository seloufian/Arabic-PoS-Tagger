# -*- coding: utf-8 -*-
from os import path
from sys import argv

from PyQt5 import QtWidgets

from include.mainWindow import MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    appDirectory = path.dirname(path.abspath(argv[0])).replace('\\', '/') + '/'
    window = MainWindow(appDirectory)
    window.show()
    exit(app.exec_())

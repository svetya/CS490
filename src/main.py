from PyQt5 import QtWidgets
from Controller.Ui_MainWindow import Ui_MainWindow

if __name__ == "__main__": 
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
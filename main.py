import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QDialog, QFileDialog
from PyQt5 import uic

QDialog, UI_Principal = uic.loadUiType("LeitorGabarito.ui")


# Define a Classe
class clsPrincipal(QDialog, UI_Principal):
    def __init__(self, parent=None):
        super(clsPrincipal, self).__init__(parent)
        self.setupUi(self)
        self.btFile.clicked.connect(self.OpenFolderDialog)


    def OpenFolderDialog(self):
        pasta = QFileDialog.getExistingDirectory(self,"./","Selecione a Pasta das Provas",QFileDialog.ShowDirsOnly)
        if pasta[0]:
            self.txtPasta.setPlainText(pasta)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = clsPrincipal(None)
    # Gasta um pouco de tempo
    ui.show()
    sys.exit(app.exec_())

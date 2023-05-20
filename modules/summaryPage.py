from PyQt6 import QtWidgets,uic


class SummaryPage(QtWidgets.QMainWindow):
    def __init__(self,summary,rouge_score):
        super().__init__()
        uic.loadUi("summary.ui",self)
        self.textBrowser.setText(summary)
        self.textBrowser_2.setText(rouge_score)
        
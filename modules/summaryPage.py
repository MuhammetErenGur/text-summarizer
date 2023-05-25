from PyQt6 import QtGui, QtWidgets,uic


class SummaryPage(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("summary.ui",self)
        self.summary = ""
        self.rouge_score = ""
        self.pushButton.clicked.connect(self.update_text)

    def update_summary(self, summary, rouge_score):
        self.summary = summary
        self.rouge_score = rouge_score


    def update_text(self):
        self.textBrowser.setPlainText(self.summary)
        self.textBrowser_2.setPlainText(self.rouge_score)
  
       
   
        
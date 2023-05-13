import os
import sys
import re
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog,QDialog, QLabel, QVBoxLayout
import networkx as nx
import matplotlib.pyplot as plt
from modules.TokenizeText import start_tokenization
from modules.SentenceScore import calculate_score
from modules.SemanticRelationship import create_threads,get_cos_similarity
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import threading
from torchmetrics.functional.text.rouge import rouge_score
from modules.plot import PlotPage
class Sentence:
    def __init__(self,sentence,sentence_score):
        self.sentence=sentence
        self.sentence_score=sentence_score



class SentenceDialog(QDialog):
    def __init__(self, sentence, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cümle özellikleri")
        layout = QVBoxLayout()
        self.sentence_label = QLabel(f"Cümle: {sentence.sentence}")
        layout.addWidget(self.sentence_label)
        self.sentence_score_label = QLabel(f"Cümle Skoru: {sentence.sentence_score}")
        layout.addWidget(self.sentence_score_label)
        self.setLayout(layout)


sentenceList=[]


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("mainwindow.ui", self)
        self.setWindowTitle("Özellik Seçim Ekranı")
        self.toolButton.clicked.connect(self.mainTextUpload)
        self.toolButton_2.clicked.connect(self.ozetTextUpload)
        self.pushButton.clicked.connect(self.create_graph_button_clicked)
        self.pushButton_2.clicked.connect(self.visualize_graph_button_clicked)
        self.textPath=""
        self.summarizedTextPath=""
        self.G = nx.DiGraph()
        self.preProccessedSentences=[]
        self.tokenizeThreadList=[]
        self.semanticRelationThreadList=[]
        self.semanticRelationRateList=[]
        self.embeddings=[]
        self.window=None
        

    

    def mainTextUpload(self):
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a file',
            directory=os.getcwd(),
        )
        self.metinText.setText(response[0])

    def ozetTextUpload(self):
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a file',
            directory=os.getcwd(),
        )
        self.ozetText.setText(response[0])



    def create_graph_button_clicked(self):
        self.textPath = self.metinText.text()
        self.summarizedTextPath= self.ozetText.text()
        f = open(self.textPath)
        lines = f.read()
        f.close()
        score_list = calculate_score(lines)
        self.relationship_Between_Sentences(lines,score_list)
    
    def visualize_graph_button_clicked(self):
        pos = nx.spring_layout(self.G,weight='weight')
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        
        if self.window is None:
            self.window = PlotPage(self.G,pos,edge_labels)
        self.window.show()

    def create_tokenize_threads(self,threadList,texts,tokenizedList,stopWords):
        wn.ensure_loaded()
        lock=threading.Lock()
        for i in range(len(texts)):
            thread = threading.Thread(target=start_tokenization, args=(texts[i],tokenizedList,lock,stopWords,))
            thread.start()
            threadList.append(thread)
        for thread in threadList:
            thread.join()


    



    def relationship_Between_Sentences(self, lines,score_list):
        sentences= re.split("\.|\n\n", lines)
        title=re.findall("^(?!.*\.).*",lines)[0]
        sentences=list(filter(lambda i: i !=''  and i != title,sentences))
        sentence = ''
        for i in range(len(sentences)):
            self.G.add_node(i+1,sentence=Sentence(sentences[i],score_list[i]))
            sentence += f"Cümle {i+1} : {sentences[i].strip()} \n"
            sentenceList.append(sentences[i])
            
        
    
        self.nodeSentence.setText(sentence)
        print("hesaplama")
        stopWords = list(set(stopwords.words('english')))
        self.create_tokenize_threads(self.tokenizeThreadList,sentenceList,self.preProccessedSentences,stopWords)
        self.embeddings=[None]*len(self.preProccessedSentences)
        create_threads(self.semanticRelationThreadList,self.preProccessedSentences,self.embeddings)
        self.semanticRelationRateList=get_cos_similarity(self.embeddings,self.preProccessedSentences)
        self.G.add_weighted_edges_from(self.semanticRelationRateList)
        



    def calculate_rouge_score(self,text,ozet):
        RG = rouge_score(text, ozet)
        return RG
    




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


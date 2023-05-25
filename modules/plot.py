from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import networkx as nx
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6 import QtWidgets,uic
from modules.summaryPage import SummaryPage
from torchmetrics.functional import rouge_score
class SentenceDialog(QDialog):
    def __init__(self, sentence, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cümle özellikleri")
        layout = QVBoxLayout()
        self.sentence_label = QLabel(f"Cümle: {sentence.sentence}")
        layout.addWidget(self.sentence_label)
        self.sentence_score_label = QLabel(f"Cümle Skoru: {sentence.sentence_score}")
        layout.addWidget(self.sentence_score_label)
        self.related_nodes_number_label = QLabel(f"Düğüme Bağlı Düğüm sayısı: {sentence.related_nodes_number}")
        layout.addWidget(self.related_nodes_number_label)
        self.setLayout(layout)


class Plot(Figure):
    def __init__(self,G,pos,edge_labels,parent=None):
        super().__init__(parent)
        self.G=G
        self.pos=pos
        self.edge_labels=edge_labels
        ax=self.add_subplot()
        nx.draw_networkx_nodes(self.G, self.pos,ax=ax)
        nx.draw_networkx_edges(self.G, self.pos,ax=ax)
        nx.draw_networkx_labels(self.G,self.pos,font_size=5,ax=ax)
        nx.draw_networkx_edge_labels(self.G,self.pos,edge_labels=self.edge_labels,font_size=5,ax=ax)

        self.canvas=FigureCanvasQTAgg(self)
        self.canvas.mpl_connect('button_press_event', lambda event: self.on_click(event,pos))
        
        
    
    def on_click(self, event,pos):
        if event.inaxes is not None:
            for node in self.G.nodes():
                x,y=pos[node]
                if x - 0.05 < event.xdata < x + 0.05 and y - 0.05 < event.ydata < y + 0.05:
                    sentence = self.G.nodes[node]["sentence"]
                    dialog =SentenceDialog(sentence)
                    dialog.exec()

class PlotPage(QtWidgets.QMainWindow):
    
    def __init__(self,G,pos,edge_labels,score_list,summarizedTextPath):
        super().__init__()
        self.window=None
        self.cid=None
        self.summary=None
        self.rouge_score=None
        self.summarizedTextPath=summarizedTextPath
        self.G_filtered=nx.Graph()
        self.G=G
        self.pos=pos
        self.edge_labels=edge_labels
        self.score_list=score_list
        uic.loadUi("plot.ui",self)
        self.fig=Plot(self.G,self.pos,self.edge_labels)
        layout=QVBoxLayout(self.widget_2)
        layout.addWidget(self.fig.canvas)
        self.setWindowTitle("Graf")
        self.pushButton.clicked.connect(self.filter_graph)
        self.pushButton_2.clicked.connect(self.create_summary)
        self.filtered_list = []

    def filter_graph(self):
        if self.cid != None:
            self.fig.canvas.mpl_disconnect(self.cid)
        sentence_score=float(self.plainTextEdit.toPlainText())
        sentence_similarity=float(self.plainTextEdit_2.toPlainText())
        
        self.filtered_list=[ n for n in self.G.nodes() if self.G.nodes[n]['sentence'].sentence_score >= sentence_score  ]
        self.G_filtered=self.G.subgraph(self.filtered_list).copy()
        self.pos = nx.spring_layout(self.G_filtered,weight='weight')
        for key, value in nx.get_edge_attributes(self.G_filtered, 'weight').items():
            if value < sentence_similarity:

                self.G_filtered.remove_edge(key[0],key[1])
        self.G_filtered=self.G_filtered.subgraph([n for n in self.G_filtered.nodes() if self.G_filtered.degree(n)>0])
        self.edge_labels = nx.get_edge_attributes(self.G_filtered, 'weight')
        self.edge_labels={key:value for key, value in self.edge_labels.items() if value >= sentence_similarity}

        sum_of_neighbors=0
        for node in self.G_filtered.nodes():
            sum_of_neighbors+=len(self.G_filtered.adj[node])
        for node in self.G_filtered.nodes():
            p1=self.score_list[node-1][0]
            p2=self.score_list[node-1][1]
            p3=self.score_list[node-1][2]
            p4=self.score_list[node-1][3]
            neighbors_number=len(self.G_filtered.adj[node])
            self.G_filtered.nodes[node]['sentence'].related_nodes_number=neighbors_number
            self.G_filtered.nodes[node]['sentence'].sentence_score=(p4+p3+((neighbors_number/sum_of_neighbors)*len(self.G_filtered.nodes())))/3*(1+(p2+p1))



        self.fig.G = self.G_filtered
        self.fig.pos = self.pos
        self.fig.edge_labels = self.edge_labels
    
        ax = self.fig.axes[0]
        ax.clear()
        nx.draw_networkx_nodes(self.G_filtered, self.pos, ax=ax)
        nx.draw_networkx_edges(self.G_filtered, self.pos, ax=ax)
        nx.draw_networkx_labels(self.G_filtered, self.pos, font_size=5, ax=ax)
        nx.draw_networkx_edge_labels(self.G_filtered, self.pos, edge_labels=self.edge_labels, font_size=5, ax=ax)
        self.cid=self.fig.canvas.mpl_connect('button_press_event', lambda event: self.on_click(event,self.pos))
        self.fig.canvas.draw()
       
    def create_summary(self):
        text = self.create_summary_text()
        f = open(self.summarizedTextPath)
        lines = f.read()
        f.close()
        print(self.window)
        if self.window is None:
            self.window = SummaryPage()
            print(self.window.summary)
            

        self.window.update_summary(text, str(self.calculate_rouge_score(text, lines)))
        self.window.show()
            # start_node=max(self.G_filtered.nodes(data=True),key=lambda score: score[1]['sentence'].sentence_score)
            
            # T = nx.algorithms.tree.maximum_spanning_tree(self.G_filtered, algorithm='prim')
            # for node in T.nodes():
            #     print(T.nodes[node]['sentence'].sentence,T.nodes[node]['sentence'].sentence_score)
            # print(f'nodes: {T.nodes(data=True)}, {T.edges(data=True)}')
            # nx.draw(T, with_labels=True)
            # plt.show()
        
        
    def create_summary_text(self):
        sentence_score_list = []
        sentence_list = []

        for node in self.G_filtered.nodes():
            sentence_score_list.append(float(self.G_filtered.nodes[node]['sentence'].sentence_score))
            sentence_list.append(self.G_filtered.nodes[node]['sentence'].sentence)

        temp_score_list = sentence_score_list

        sort_list_index = []
        i = 0
        while i < len(temp_score_list):
            index = i
            max = temp_score_list[i]
            j = 0
            while j < len(temp_score_list):
                if max <= temp_score_list[j]:
                    index = j
                    max = temp_score_list[j]
                j += 1
            sort_list_index.append(index)
            temp_score_list[index] = 0
            i += 1
        text = ''
        for i in sort_list_index:
            text += sentence_list[i] + '. '
        return text



    def calculate_rouge_score(self,text,ozet):
        RG = rouge_score(text, ozet)
        return RG
    

    def on_click(self, event,pos):
        if event.inaxes is not None:
            for node in self.G_filtered.nodes():
                x,y=pos[node]
                if x - 0.05 < event.xdata < x + 0.05 and y - 0.05 < event.ydata < y + 0.05:
                    sentence = self.G.nodes[node]["sentence"]
                    dialog =SentenceDialog(sentence)
                    dialog.exec()
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import networkx as nx
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6 import QtWidgets,uic

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
    
    def __init__(self,G,pos,edge_labels):
        super().__init__()
        self.cid=None
        self.G_filtered=nx.DiGraph()
        self.G=G
        self.pos=pos
        self.edge_labels=edge_labels
        uic.loadUi("plot.ui",self)
        self.fig=Plot(self.G,self.pos,self.edge_labels)
        layout=QVBoxLayout(self.widget_2)
        layout.addWidget(self.fig.canvas)
        self.setWindowTitle("Graf")
        self.pushButton.clicked.connect(self.filter_graph)
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
       
        
    def on_click(self, event,pos):
        if event.inaxes is not None:
            for node in self.G_filtered.nodes():
                x,y=pos[node]
                if x - 0.05 < event.xdata < x + 0.05 and y - 0.05 < event.ydata < y + 0.05:
                    sentence = self.G.nodes[node]["sentence"]
                    dialog =SentenceDialog(sentence)
                    dialog.exec()
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
        uic.loadUi("plot.ui",self)
        self.fig=Plot(G,pos,edge_labels)
        layout=QVBoxLayout(self.widget_2)
        layout.addWidget(self.fig.canvas)
        self.setWindowTitle("Graf")



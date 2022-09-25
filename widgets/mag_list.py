from select import select
import PyQt5.QtWidgets as Qtw
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor

"""
The displayed list of magnetic objects.
"""


class MagneticObjectsList(Qtw.QListWidget):
    
    def __init__(self, parent, on_delete, on_hide) -> None:
        super().__init__(parent)
        
        self.on_delete = on_delete
        self.on_hide = on_hide
        
        self.hidden_items = []
    
    def get_selected_obj_id(self):
        selected_data = self.currentIndex().data()
        if not selected_data:
            return None

        return float(selected_data.split('-')[1])
        
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if not self.currentIndex().data():
            return 
        
        selected_id = int(self.currentIndex().data().split('-')[1])

        if e.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            # Remove the item from the list.
            self.takeItem(self.currentRow())
            self.on_delete(selected_id)
            
        elif e.key() == Qt.Key_H:
            if selected_id not in self.hidden_items:
                self.hidden_items.append(selected_id)
                self.currentItem().setBackground(QColor(255, 0,169,100))
            else:
                self.hidden_items.remove(selected_id)
                self.currentItem().setBackground(QColor(0, 0,0,0))

            self.on_hide(selected_id)
            
        return super().keyPressEvent(e)
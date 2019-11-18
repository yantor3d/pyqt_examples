"""Sort/Filter Proxy Model example."""

import json
import os
import random
import sys
import functools

from PySide2 import QtCore, QtGui, QtWidgets 

random.seed(42)

COLORS = {
    'Black': QtGui.QColor(QtCore.Qt.black),
    'Red': QtGui.QColor(QtCore.Qt.red),
    'Dark Red': QtGui.QColor(QtCore.Qt.darkRed),
    'Green': QtGui.QColor(QtCore.Qt.green),
    'Dark Green': QtGui.QColor(QtCore.Qt.darkGreen),
    'Blue': QtGui.QColor(QtCore.Qt.blue),
    'Dark Blue': QtGui.QColor(QtCore.Qt.darkBlue),
    'Cyan': QtGui.QColor(QtCore.Qt.cyan),
    'Dark Cyan': QtGui.QColor(QtCore.Qt.darkCyan),
}

COLOR_NAMES = list(COLORS.keys())


class SourceModel(QtGui.QStandardItemModel):
    Changed = QtCore.Signal()

    def __init__(self):
        super(SourceModel, self).__init__()

        data_filepath = os.path.join(os.path.dirname(__file__), 'data.json')

        with open(data_filepath, 'r') as fp:
            self.words = json.load(fp)

    def refresh(self):
        self.clear()

        for i in range(1000):
            self._make_data_item()

        self.Changed.emit()

    def _make_data_item(self):
        name = ' '.join(random.choices(self.words, k=3))
        color = random.choice(COLOR_NAMES)

        item = ColorItem(name, color)

        self.appendRow(item)


class ProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self):
        super(ProxyModel, self).__init__()

        self._filter_value = None 

        self.setFilterRole(QtCore.Qt.UserRole + 1)
        self.sort(0)

    @property
    def sort_role(self):
        return self.sortRole()

    @sort_role.setter 
    def sort_role(self, value):        
        self.setSortRole(value)

    @property
    def filter_string(self):
        return self.filterFixedString()

    @filter_string.setter
    def filter_string(self, value):
        self.setFilterFixedString(value)
        self.invalidate()

    @property 
    def filter_value(self):
        return self._filter_value

    @filter_value.setter
    def filter_value(self, value):
        self._filter_value = value 
        self.invalidate()

    def refresh(self):
        self.sourceModel().refresh()

        # Calling `invalidate` re-runs the filter and ensures a `layoutChanged`
        # signal is emitted by the model proxy.
        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        # The default behavior of a sort/filter proxy model will filter 
        # items using the filter string. Additional filters, like one to
        # filter by color, need to implemented on top of this behavior.

        if self.filter_value is not None:
            source_index = self.sourceModel().index(
                source_row, 0, source_parent
            )
            item = self.sourceModel().itemFromIndex(source_index)
            result = self.filter_value == item.color
        else:
            result = True 

        if result:
            result = super(ProxyModel, self).filterAcceptsRow(
                source_row, source_parent
            )

        return result 

    def item_from_index(self, index):
        # A sort/filter proxy model manages its own indices that must be
        # mapped to the indices of the source model to access the items
        source_index = self.mapToSource(index)
        return self.sourceModel().itemFromIndex(source_index)


class ItemView(QtWidgets.QListView):
    def __init__(self, model, parent=None):
        super(ItemView, self).__init__(parent)

        self.setSelectionMode(QtWidgets.QTreeView.SingleSelection)
        self.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setMovement(QtWidgets.QListView.Static)
        self.setIconSize(QtCore.QSize(96, 96))
        self.setLayoutMode(QtWidgets.QListView.Batched)
        self.setModel(model)

    def selectionChanged(self, old, new):
        for index in self.selectedIndexes():
            item = self.model().item_from_index(index)

            print(
                '{:12} {}'
                .format('[{}]'.format(item.color), item.name)
            )


class ColorItem(QtGui.QStandardItem):
    """Model item for a color swatch."""

    # Wrapping QStandardItem provides a pythonic API for accessing the data 
    # (eg, item.color) instead of having to make other objects aware of the 
    # data role values.

    NAME_ROLE = QtCore.Qt.UserRole + 1
    COLOR_ROLE = QtCore.Qt.UserRole + 2

    def __init__(self, name, color):
        display_name = name.replace(' ', '\n')

        super(ColorItem, self).__init__(display_name)
        
        self.setData(name, self.NAME_ROLE)
        self.setData(color, self.COLOR_ROLE)

        color_swatch = COLORS[color]
        self.setData(color_swatch, QtCore.Qt.DecorationRole)

    @property 
    def name(self):
        return self.data(self.NAME_ROLE)

    @property
    def color(self):
        return self.data(self.COLOR_ROLE)


class SimpleDataModel(QtGui.QStandardItemModel):
    """Simple wrapper around a QStandardItemModel.
    
    Allows construction of items with data in a fixed role.
    """

    def __init__(self, data_role=QtCore.Qt.UserRole + 1):
        super(SimpleDataModel, self).__init__()
        self.data_role = data_role

    def _add_item(self, name, data):
        item = QtGui.QStandardItem(name)
        item.setData(data, self.data_role)

        self.appendRow(item)


class Colors(SimpleDataModel):
    """List of color options."""

    def __init__(self):
        super(Colors, self).__init__()
        
        self._add_item('All Colors', None)

        for color in sorted(COLORS):
            self._add_item(color, color)


class SortModes(SimpleDataModel):
    """List of sort options."""

    def __init__(self):
        super(SortModes, self).__init__()

        self._add_item('By Name', ColorItem.NAME_ROLE)
        self._add_item('By Color', ColorItem.COLOR_ROLE)


class DataComboBox(QtWidgets.QComboBox):
    """Simple wrapper around a ComboBox.
    
    The `Changed` signal emits the data assigned to the selected item.
    """

    Changed = QtCore.Signal(object)

    def __init__(self, model, parent=None, data_role=QtCore.Qt.UserRole + 1):
        self.data_role = data_role 

        super(DataComboBox, self).__init__(parent)
        
        self.currentIndexChanged.connect(self._handle_index_changed)
        self.setModel(model)

    def _handle_index_changed(self, index):
        self.Changed.emit(self.itemData(index, self.data_role))
        

class MainWidget(QtWidgets.QWidget):
    """Widget for viewing a list of items, with filter/sort capabilities."""

    def __init__(self, model, parent=None):
        super(MainWidget, self).__init__(parent)

        self.model = model 

        main_layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()

        self.filter_edit = QtWidgets.QLineEdit(self)
        self.sort_mode = DataComboBox(SortModes(), self)
        self.color_mode = DataComboBox(Colors(), self)
        self.flow_view = ItemView(model, self)       
        self.item_count = QtWidgets.QLabel()

        form_layout.addRow('Search', self.filter_edit)
        form_layout.addRow('Sort', self.sort_mode)
        form_layout.addRow('Show', self.color_mode)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.flow_view)
        main_layout.addWidget(self.item_count)
        
        self._connect_slots()

    def _connect_slots(self):
        """Connect signals/slots."""

        self.model.layoutChanged.connect(self._update_item_count)

        # A partial of `setattr` gives you a callable to assign a value.
        #
        # f = partial(setattr, obj, 'foo')
        # f(5)
        # obj.foo
        # 5

        self.filter_edit.textChanged.connect(
            functools.partial(setattr, self.model, 'filter_string')
        )

        self.sort_mode.Changed.connect(
            functools.partial(setattr, self.model, 'sort_role')
        )

        self.color_mode.Changed.connect(
            functools.partial(setattr, self.model, 'filter_value')
        )

    def _update_item_count(self):        
        """Update the item counter."""

        self.item_count.setText(
            'Showing {:4d} Items'
            .format(self.model.rowCount())
        )


class MainWindow(QtWidgets.QMainWindow):    
    """Tool for viewing a list of items, with filter/sort capabilities."""

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('Filter/Sort Proxy Model Example')

        self.model = ProxyModel()
        self.model.setSourceModel(SourceModel())

        self.setCentralWidget(MainWidget(self.model))

        self._opened = False 

    def showEvent(self, event):
        super(MainWindow, self).showEvent(event)

        if not self._opened:
            self._opened = True 

            QtCore.QTimer.singleShot(10, self.refresh)

    def refresh(self):
        """Refresh the view."""

        self.model.refresh()


def main():
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(True)

    win = MainWindow()
    win.resize(540, 400)
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
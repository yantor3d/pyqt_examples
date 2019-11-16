"""Advanced model/view example.

This example shows the model/view to rendering nested data in a tree structure,
shared across multiple widgets.
"""

import os
import operator
import sys 

import common 

from PySide2 import QtCore, QtGui, QtWidgets


class StatusView(QtWidgets.QTreeView):
    """Widget that displays the status of items."""

    def __init__(self, model, parent=None):
        """Initialize.
        
        Args:
            model (QtGui.QStandardItemModel): Model for the item/status data.
            parent (QtWidgets.QWidget): Parent widget for this widget.
        """

        super(StatusView, self).__init__(parent)

        self.setSelectionMode(QtWidgets.QTreeView.NoSelection)
        self.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
        self.setModel(model)


class RootLeafWidget(QtWidgets.QWidget):
    """Widget to select root/leaf items."""

    IndexChanged = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, model, parent=None):
        """Initialize.
        
        Args:
            model (QtGui.QStandardItemModel): Model for the root/leaf data.
            parent (QtWidgets.QWidget): Parent widget for this widget.
        """

        super(RootLeafWidget, self).__init__(parent)

        form_layout = QtWidgets.QFormLayout(self)

        # A QComboBox behaves like a QListView 
        # that renders only the selected item.
        self.sel_root = QtWidgets.QComboBox(self)
        self.sel_root.setModel(model)
        self.sel_root.currentIndexChanged.connect(self._handle_root_changed)

        self.sel_leaf = QtWidgets.QComboBox(self)
        self.sel_leaf.setModel(model)
        self.sel_leaf.currentIndexChanged.connect(self._handle_leaf_changed)

        form_layout.addRow('Root', self.sel_root)
        form_layout.addRow('Leaf', self.sel_leaf)

    def _handle_root_changed(self, row):
        """Handle the user selecting a root item.

        Args:
            row (int): Selected row in the combo box.
        """

        # When the root is selected, we need to point the leaf combo box at 
        # the index for that root so the correct leaf items are shown.
        new_index = self.sel_root.model().index(row, 0)

        self._set_root_index(self.sel_leaf, new_index, restore_selection=True)

    def _handle_leaf_changed(self, row):
        """Handle the user selecting a leaf item.

        Args:
            row (int): Selected row in the combo box.
        """

        # When a leaf is selected, we need to point the tree view at 
        # the index for that root so the items are shown. Note that the 
        # new index is a child of the leaf index, because our data model
        # is hierarchical.
        new_index = self.sel_leaf.model().index(
            row, 0, self.sel_leaf.rootModelIndex()
        )

        self.IndexChanged.emit(new_index)

    @staticmethod
    def _set_root_index(combobox, index, restore_selection=True):
        """Set the root index of the given combobox.

        Args:
            combobox (QtWidgets.QComboBox): Combobox to edit.
            index (QtCore.QModelIndex): New root index for the combobox.
            restore_selection (bool): If True, attempt to restore the combo box
                to the last selected row. If the index is out of bounds, set 
                the selection to the first row.
        """

        # Setting a new model/root index in a combo box clears the selection.
        # We can either reset to the first item, or try to maintain selection.
        # In this example, we just re-select the same index, but in production
        # code, you would have to some sort of lookup to find the index of the 
        # "same" item (eg, same name, same data, etc).
        row = combobox.currentIndex()
        combobox.setRootModelIndex(index)

        if restore_selection:
            row = max(0, row * (row < combobox.count()))
            combobox.setCurrentIndex(row)
        else:
            combobox.setCurrentIndex(0)


class StatusWidget(QtWidgets.QWidget):
    """Widget that displays the status of items."""

    def __init__(self, parent=None):
        """Initialize.
        
        Args:
            parent (QtWidgets.QWidget): Parent widget for this widget.
        """

        super(StatusWidget, self).__init__(parent)

        # Normally, the model should be passed to the view; this is just an 
        # artifact of how I set up the re-usable components of this example.
        # 
        # Passing the model to the view means you can mock it when your doing 
        # tests/demos if you don't want to deal with spinning up a test database
        # and populating test data.
        self.model = StatusModel()

        # Decomposing your view into individual widgets makes your code easier 
        # to digest in small junks. Let the widget be responsible for its own
        # static configuration options.
        self.status_view = StatusView(self.model, self)

        # A GroupBox lets you organize and label your widgets.
        self.status_box = QtWidgets.QGroupBox('Status')
        self.status_lay = QtWidgets.QVBoxLayout(self.status_box)
        self.status_lay.addWidget(self.status_view)

        # Decomposing your view into individual widgets also them re-usable.
        # How many tools do you have that have your user select a data in a 
        # parent/child relationship? Hint: do you group shots by sequence?
        self.sel_widget = RootLeafWidget(self.model, self)
        self.sel_widget.IndexChanged.connect(self.status_view.setRootIndex)

        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.addWidget(self.sel_widget)
        root_layout.addWidget(self.status_box)
    
    def refresh(self):
        """Refresh the UI."""

        self.model.refresh()


class StatusModel(QtGui.QStandardItemModel):
    """Provides access to the status of items."""

    def refresh(self):
        """Refresh the list of status items in this model."""

        data = common.query_db('data2.json')

        self.clear()

        # In a Model/View setup, the model is responsible for the header labels.
        self.setHorizontalHeaderLabels(['Name', 'Status'])

        # Use the operator module to make callables that behave like operators
        # For example, operator.itemgetter('foo')(obj) is the same as obj.foo
        for each in sorted(data, key=operator.itemgetter('name')):
            self._create_item_a(each, self)

    def _create_item_a(self, data, parent):
        """Create a item for the status list.

        Args:
            data (dict): Status data.
            parent (QtGui.QStandardItemModel): Parent for the model items.
        """

        item = QtGui.QStandardItem(data['name'])

        for each in sorted(data.get('items', []), key=operator.itemgetter('name')):
            self._create_item_b(each, item)
        
        parent.appendRow(item)

    def _create_item_b(self, data, parent):
        """Create a named item for the status list.

        Args:
            data (dict): Status data.
            parent (QtGui.QStandardItem): Parent for the model items.
        """

        item = QtGui.QStandardItem(data['name'])

        for each in data.get('items', []):
            self._create_item_c(each, item)
        
        parent.appendRow(item)

    def _create_item_c(self, data, parent):
        """Create a child item for the status list.

        Args:
            data (dict): Status data.
            parent (QtGui.QStandardItem): Parent for the model items.
        """

        name = data['name']
        status = data['status']

        name_item = QtGui.QStandardItem(name)
        status_item = QtGui.QStandardItem(common.STATUS_NAMES.get(status))

        # The constructor of QStandardItem accepts the text/display data.
        # You can set additional internal data on the item in any "role".
        status_item.setData(status)

        brush = QtGui.QBrush(common.STATUS_COLORS[status])
        name_item.setBackground(brush)
        status_item.setBackground(brush)

        parent.appendRow([name_item, status_item])


def main():
    common.main(
        widget=StatusWidget,
        window_name='Model/View+'
    )


if __name__ == '__main__':
    main()

"""Tree model/view example.

This example shows the model/view to rendering a data in a tree structure. 
It uses a QTreeView and QStandardItemModel
"""

import os
import sys 

import common 

from PySide2 import QtCore, QtGui, QtWidgets


class StatusView(QtWidgets.QTreeView):
    """View that displays the status of items."""

    def __init__(self, parent=None):
        """Initialize.
        
        Args:
            parent (QtWidgets.QWidget): Parent widget for this widget.
        """

        super(StatusView, self).__init__(parent)

        self.setSelectionMode(QtWidgets.QTreeView.SingleSelection)
        self.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
        self.setModel(StatusModel())

    @property
    def selected_index(self):
        """Return the index of the selected item.
        
        Returns:
            QtCore.QModelIndex
        """

        return (self.selectedIndexes() or [QtCore.QModelIndex()])[0]

    def refresh(self):
        """Refresh the status view."""

        self.model().refresh()

        self.expandAll()
        self.setItemsExpandable(False)

        for row in self.model().rows:
            self.setFirstColumnSpanned(row, QtCore.QModelIndex(), True)

    def selectionChanged(self, selected, deselected):
        """Handle the user selecting an item in the status view."""

        try:
            item_status = self.model()[self.selected_index]
        except IndexError:
            pass
        else:
            common.print_item_status(item_status)


class StatusModel(QtGui.QStandardItemModel):
    """Provides access to the status of items."""

    @property 
    def rows(self):
        """Return the row indices for this model.
        
        Returns:
            iterable[int]
        """

        return range(self.rowCount())

    def __getitem__(self, index):
        """Return the status for the item at the given index.

        Args:
            index (QtCore.QModelIndex): Index of an item.
        
        Returns:
            ItemStatus

        Raises:
            IndexError: If the index is invalid.
        """

        if not index.isValid():
            raise IndexError()

        if not index.parent().isValid():
            raise IndexError()

        return common.ItemStatus(
            self.itemFromIndex(index.siblingAtColumn(0)).text(),
            self.itemFromIndex(index.parent()).text(),
            self.itemFromIndex(index.siblingAtColumn(1)).data(),
        )

    def flags(self, index):
        """Return the flags for the item at the given index.

        Args:
            index (QtCore.QModelIndex): Index of an item.
        
        Returns:
            QtCore.Qt.ItemFlags
        """

        result = super(StatusModel, self).flags(index)

        is_top_level_item = index.isValid() and not index.parent().isValid()

        if is_top_level_item:
            result &= ~QtCore.Qt.ItemIsSelectable

        return result 

    def refresh(self):
        """Refresh the list of status items in this model."""

        data = common.query_db()

        self.clear()
        self.setHorizontalHeaderLabels(['Name', 'Status'])

        for name, items in sorted(data.items()):
            self._create_top_item(name, items, self)

    def _create_top_item(self, name, data, parent):
        """Create a top level item for the status list.

        Args:
            name (str): Display name of the top level item.
            data (list(dict]): Status item data.
            parent (QtGui.QStandardItemModel): Parent for the item.
        """

        top_item = QtGui.QStandardItem(name)

        for child, status in sorted(data.items()):
            self._create_child_items(child, status, top_item)
        
        parent.appendRow(top_item)

    def _create_child_items(self, name, status, parent):
        """Create a child item for the status list.

        Args:
            name (str): Display name of the child item.
            status (str): Status code for the child item.
            parent (QtGui.QStandardItem): Parent for the item.
        """

        child_item = QtGui.QStandardItem(name)
        status_item = QtGui.QStandardItem(common.STATUS_NAMES.get(status))
        status_item.setData(status)

        brush = QtGui.QBrush(common.STATUS_COLORS[status])
        child_item.setBackground(brush)
        status_item.setBackground(brush)

        parent.appendRow([child_item, status_item])


def main():
    common.main(
        widget=StatusView,
        window_name='Model/View'
    )


if __name__ == '__main__':
    main()

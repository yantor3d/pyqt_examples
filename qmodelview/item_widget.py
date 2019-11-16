"""Tree item/widget example.

This example shows the widget approach to rendering a data in a tree structure. 
It uses a QTreeWidget and QTreeWidgetItems.
"""

import os
import sys 

import common 

from PySide2 import QtCore, QtGui, QtWidgets


class StatusWidget(QtWidgets.QTreeWidget):
    """Widget that displays the status of items."""

    def __init__(self, parent=None):
        """Initialize.
        
        Args:
            parent (QtWidgets.QWidget): Parent widget for this widget.
        """

        super(StatusWidget, self).__init__(parent)

        self.setColumnCount(2)
        self.setHeaderLabels(['Name', 'Status'])
        self.setSelectionMode(QtWidgets.QTreeWidget.SingleSelection)
        self.itemSelectionChanged.connect(self._handle_item_selection_handled)

    def refresh(self):
        """Refresh the list of status items."""

        data = common.query_db()
        
        self.clear()

        for name, items in sorted(data.items()):
            self._create_top_item(name, items, self)

        self.expandAll()

    def _create_top_item(self, name, data, parent):
        """Create a top level item for the status list.

        Args:
            name (str): Display name of the top level item.
            data (list(dict]): Status item data.
            parent (QtWidgets.QTreeWidget): Parent for the item.
        """

        top_item = QtWidgets.QTreeWidgetItem(parent)
        top_item.setFlags(top_item.flags() & ~QtCore.Qt.ItemIsSelectable)
        top_item.setChildIndicatorPolicy(
            QtWidgets.QTreeWidgetItem.DontShowIndicatorWhenChildless
        )
        top_item.setText(0, name)

        for child, status in sorted(data.items()):
            self._create_child_item(child, status, top_item)

    def _create_child_item(self, name, status, parent):
        """Create a child item for the status list.

        Args:
            name (str): Display name of the child item.
            status (str): Status code for the child item.
            parent (QtWidgets.QTreeWidgetItem): Parent for the item.
        """

        child_item = QtWidgets.QTreeWidgetItem(parent)
        brush = QtGui.QBrush(common.STATUS_COLORS[status])
        child_item.setBackground(0, brush)
        child_item.setBackground(1, brush)
        child_item.setText(0, name)
        child_item.setText(1, common.STATUS_NAMES.get(status))
        child_item.setData(1, QtCore.Qt.UserRole, status)
        
    def _handle_item_selection_handled(self):
        """Handle the user selecting an item in the status list."""

        item, = self.selectedItems() or [None]

        if item is None:
            return

        item_status = self._item_status(item)
        common.print_item_status(item_status)

    def _item_status(self, item):
        """Return the status for the given item.

        Args:
            item (QtWidgets.QTreeWidgetItem): Status item.
        
        Returns:
            ItemStatus
        """

        return common.ItemStatus(
            item.parent().text(0),
            item.text(0),
            item.data(1, QtCore.Qt.UserRole)
        )


def main():
    common.main(
        widget=StatusWidget,
        window_name='Item/Widget'
    )


if __name__ == '__main__':
    main()

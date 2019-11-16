import collections
import json
import os
import sys 

from PySide2 import QtCore, QtGui, QtWidgets


STATUS_NAMES = {
    'rdy': 'Ready to Start',
    'omt': 'Omitted',
    'wip': 'In Progress',
    'fin': 'Final'
}

STATUS_COLORS = {
    'rdy': QtCore.Qt.white,
    'omt': QtCore.Qt.darkGray,
    'wip': QtCore.Qt.yellow,
    'fin': QtCore.Qt.green
}

ItemStatus = collections.namedtuple('ItemStatus', 'parent child status')


def print_item_status(item_status):
    print('{parent}:{child} ({status})'.format(**item_status._asdict()))


def query_db():
    with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'r') as fp:
        return json.load(fp)


class StatusWindow(QtWidgets.QMainWindow):
    """Window for a tool that displays the status of items."""

    def __init__(self, widget):
        """Initialize."""

        super(StatusWindow, self).__init__()

        self._status_widget = widget(self)
        self.setCentralWidget(self._status_widget)
        self.setFixedWidth(320)
        self.setFixedHeight(320)

        self._opened = False

    def showEvent(self, event):
        # Delay "querying" the DB until after the window has opened
        if not self._opened:
            self._opened = True 
            self._handle_window_opened()

        super(StatusWindow, self).showEvent(event)

    def _handle_window_opened(self):
        """Handle the window opening for the first time."""

        self._status_widget.refresh()


def main(widget, window_name):
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(True)

    win = StatusWindow(widget)
    win.setWindowTitle('{} Work Status'.format(window_name))
    win.show()

    sys.exit(app.exec_())
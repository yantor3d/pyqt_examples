"""Window example."""

import sys 

from PySide2 import QtCore, QtGui, QtWidgets


class MyWidget(QtWidgets.QDialog):
    """A simple example widget."""

    Order = QtCore.Signal(str)

    def __init__(self, parent=None):
        """Initialize.

        Args:
            parent (PySide2.QtWidgets.QWidget): Parent widget for this dialog.
        """

        super(MyWidget, self).__init__(parent)

        self.option_a = QtWidgets.QCheckBox('Chips and Guac')
        self.option_b = QtWidgets.QCheckBox('Chips and Queso')
        self.option_c = QtWidgets.QCheckBox('Chips and Salsa')

        self.accept_btn = QtWidgets.QPushButton('Add to Order')

        self.button_group = QtWidgets.QButtonGroup()

        options_box = QtWidgets.QGroupBox('Options')
        options_lay = QtWidgets.QVBoxLayout(options_box)
        options_lay.addWidget(self.option_a)
        options_lay.addWidget(self.option_b)
        options_lay.addWidget(self.option_c)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.accept_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(options_box)
        layout.addLayout(btn_layout)

        self._setup()

    def _setup(self):
        """Set up the signal/slot connections."""

        self.accept_btn.clicked.connect(self._handle_accept_clicked)

        self.button_group.addButton(self.option_a)
        self.button_group.addButton(self.option_b)
        self.button_group.addButton(self.option_c)

        self.button_group.setExclusive(True)
        self.option_a.setChecked(True)

    def _handle_accept_clicked(self):
        """Handle the user clicking 'Accept'."""

        item = self.button_group.checkedButton().text()

        self.Order.emit(item)


def main():
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(True)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle('Sides')
    win.setCentralWidget(MyWidget())
    win.show()

    def handle_order(item):
        print('# You ordered a side of {}'.format(item.lower()))

    win.centralWidget().Order.connect(handle_order)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
"""Dialog example."""

import sys 

from PySide2 import QtCore, QtGui, QtWidgets


class PromptDialog(QtWidgets.QDialog):
    """A simple example dialog."""

    def __init__(self, title='Prompt', message='Enter text:', parent=None):
        """Initialize.

        Args:
            parent (PySide2.QtWidgets.QWidget): Parent widget for this dialog.
        """

        super(PromptDialog, self).__init__(parent)

        self.setWindowTitle(title)

        self._text_field = QtWidgets.QLineEdit(self)
        self._buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            parent=self
        )

        layout = QtWidgets.QFormLayout(self)
        layout.addRow(message, self._text_field)
        layout.addRow(self._buttons)

        self._setup()

    def _setup(self):
        """Set up the signal/slot connections."""

        self._buttons.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        self._text_field.textChanged.connect(self._handle_text_changed)

    @property
    def text(self):
        """Return the text the user entered."""
 
        return self._text_field.text()

    def _handle_text_changed(self, text):
        """Enable the OK button if the user has entered text."""

        self._buttons.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(bool(text))


def main():
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(True)

    dlg = PromptDialog()
    dlg.resize(240, 60)

    if dlg.exec_():
        print("# Accepted - Result: '{}'".format(dlg.text))
    else:
        print("# Canceled - No result")

    sys.exit(0)


if __name__ == '__main__':
    main()
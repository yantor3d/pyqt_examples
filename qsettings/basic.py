"""Settings dialog basic example.

This example shows the straight forward approach to using a QSettings class for 
persisting user preferences and tool settings between sessions. It involves a 
great deal more boilerplate code.
"""

import sys 

from PySide2 import QtCore, QtGui, QtWidgets


class SettingsModel(QtCore.QSettings):
    """Settings model.

    Use the Settings descriptor to create attributes to get/set the values.
    """

    def __init__(self):
        super(SettingsModel, self).__init__(
            QtCore.QSettings.IniFormat, 
            QtCore.QSettings.UserScope, 
            'Yantor3D', 
            'BasicSettingsDialog'
        )

    @property 
    def color(self):
        return self.value('color', default='red')

    @color.setter 
    def color(self, value):
        self.setValue('color', value)

    @property 
    def toggle(self):
        return int(self.value('toggle', default=0))

    @toggle.setter 
    def toggle(self, value):
        self.setValue('toggle', int(value))


class RadioButtonGroup(QtWidgets.QWidget):
    """Radio button group widget.

    Presents the user with the choice of items to choose from. Exactly one item may be chosen at a time.
    """

    def __init__(self, label, value, model, parent=None):
        """Initialize.

        Args:
            label (str): Label for the radio button group.
            value (Any): The default selection for this group.
            model (QStandardItemModel): Items to choose from. The .text() value is displayed; the .data() value is set.
            parent (QWidget): Optional parent for this widget.
        """

        super(RadioButtonGroup, self).__init__(parent)

        self._model = model

        self.button_group = QtWidgets.QButtonGroup(self)

        box = QtWidgets.QGroupBox(label, self)
        lay = QtWidgets.QVBoxLayout(box)
        root = QtWidgets.QVBoxLayout(self)
        root.addWidget(box)

        for index in range(self._model.rowCount()):
            item = self._model.item(index)

            button = QtWidgets.QRadioButton(item.text(), self)
            button.setChecked(item.data() == value)
            self.button_group.addButton(button, index)

            lay.addWidget(button)

        self.button_group.setExclusive(True)

    @property 
    def value(self):
        index = self.button_group.checkedId()
        item = self._model.item(index)

        return item.data()


class SettingsDialog(QtWidgets.QDialog):
    """Simple dialog for editing settings."""

    def __init__(self, settings):
        """Initialize.

        Args:
            settings (SettingsModel): Settings to edit.
        """

        super(SettingsDialog, self).__init__()

        self._settings = settings 

        self.setWindowTitle('Basic Settings')

        layout = QtWidgets.QVBoxLayout(self)

        self.select_color = RadioButtonGroup('Color', self._settings.color, self.colors(), self)

        self.checkbox = QtWidgets.QCheckBox('Checkbox', self)
        self.checkbox.setChecked(self._settings.toggle)

        layout.addWidget(self.select_color)
        layout.addWidget(self.checkbox)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def colors(self):
        model = QtGui.QStandardItemModel()

        for color in ['red', 'blue', 'green']:
            item = QtGui.QStandardItem(color.capitalize())
            item.setData(color)
            model.appendRow(item)

        return model 

    def accept(self):
        self._settings.color = self.select_color.value
        self._settings.toggle = self.checkbox.isChecked()

        self._settings.sync()

        super(SettingsDialog, self).accept()


def main():
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(True)

    settings = SettingsModel()

    dialog = SettingsDialog(settings)
    dialog.exec_()

    sys.exit()


if __name__ == '__main__':
    main()
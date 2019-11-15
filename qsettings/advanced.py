"""Settings dialog advanced example.

This example shows the an advanced approach to using a QSettings class for 
persisting user preferences and tool settings between sessions. It uses 
descriptors and partials to eliminate most of the boilerplate.
"""

import collections
import sys 

import functools

from PySide2 import QtCore, QtGui, QtWidgets

SettingsEditor = collections.namedtuple('SettingsEditor', 'get set')


class SettingsModelProxy(object):
    """Settings model proxy.

    This model allows edits to be made to the settings without modifying the 
    values until the changes are comitted.
    """

    def __init__(self, settings):
        """Initialize.

        Args:
            settings (QSettings): Settings to edit.
        """

        self._settings = settings 
        self._edits = {}

    def editor(self, attr):
        """Return an pair of editor functions (get/set) for the given attribute.

        Args:
            attr (str): Name of the attribute to editor.

        Returns:
            SettingsEditor
        """

        assert hasattr(self._settings, attr), \
            "The {} has no attribute '{}'".format(self.__class__.__name__, attr)

        return SettingsEditor(
            functools.partial(getattr, self._settings, attr),
            functools.partial(self._edits.__setitem__, attr)
        )

    def sync(self):
        """Commit the edits to the settings model."""

        for key, value in self._edits.items():
            self.setValue(key, value)
    
        self._settings.sync()

    def setValue(self, key, value):        
        """Set the value of the given key.
        
        Args:
            key (str): Key to set the value of.
            value (Any): New value to set the key to.
        """

        setattr(self._settings, key, value)

    def value(self, key, defaultValue=None):      
        """Return the value for the given key.

        Args:
            key (str): Key to get the value of.
            defaultValue (Any): Default value to return if no value is set.
        
        Returns:
            Any
        """

        getattr(self._settings, key, defaultValue)


class Setting(object):  
    """QSettings value descriptor.
        
    This descriptor handles the boiler plate to get/set a value on a 
    QSettings-like object. The bound object must have these methods:
        def setValue(self, key, value)
        def value(self, key[, defaultValue=None])
    """

    def __init__(self, key, default=None, get_as_type=None, set_as_type=None):
        """Initialize.

        Args:
            key (str): Key to access the settings in the QSettings object.
            default (Any): Optional default value for the settings.
            get_as_type (callable): Optional convert function for get.
            set_as_type (callable): Optional convert function for set.
        """

        self.key = key 
        self.default = default 
        self.get_as_type = get_as_type
        self.set_as_type = set_as_type

    def __get__(self, obj, type=None):
        value = obj.value(self.key, self.default)

        if callable(self.get_as_type):
            value = self.get_as_type(value)

        return value

    def __set__(self, obj, value):
        if callable(self.set_as_type):
            value = self.set_as_type(value)

        obj.setValue(self.key, value)


class SettingsModel(QtCore.QSettings):
    """Settings model.

    Use the Settings descriptor to create attributes to get/set the values.
    """

    color = Setting('color', default='red')
    toggle = Setting('toggle', default=False, get_as_type=int, set_as_type=int)

    def __init__(self):
        super(SettingsModel, self).__init__(
            QtCore.QSettings.IniFormat, 
            QtCore.QSettings.UserScope, 
            'Yantor3D', 
            'AdvancedSettingsDialog'
        )

    def editor(self, attr):
        """Return an pair of editor functions (get/set) for the given attribute.

        Args:
            attr (str): Name of the attribute to editor.

        Returns:
            SettingsEditor
        """

        assert hasattr(self._settings, attr), \
            "The {} has no attribute '{}'".format(self.__class__.__name__, attr)

        return SettingsEditor(
            functools.partial(getattr, self._settings, attr),
            functools.partial(setattr, self._settings, attr)
        )


class CheckBox(QtWidgets.QCheckBox):
    """Checkbox widget.

    Presents the user with an option to toggle on/off.
    """

    def __init__(self, label, editor, parent=None):
        """Initialize.

        Args:
            label (str): Label for the check box.
            editor (SettingsEditor): Editor for the value being changed.
            parent (QWidget): Optional parent for this widget.
        """

        super(CheckBox, self).__init__(label, parent)

        self._editor = editor 

        self.setChecked(self._editor.get())
        self.stateChanged.connect(self._handle_change)
    
    def _handle_change(self, state):
        self._editor.set(self.isChecked())


class RadioButtonGroup(QtWidgets.QWidget):
    """Radio button group widget.

    Presents the user with the choice of items to choose from. Exactly one item may be chosen at a time.
    """

    def __init__(self, label, editor, model, parent=None):
        """Initialize.

        Args:
            label (str): Label for the radio buttons.
            editor (SettingsEditor): Editor for the value being changed.
            model (QStandardItemModel): Items to choose from. The .text() value is displayed; the .data() value is set.
            parent (QWidget): Optional parent for this widget.
        """

        super(RadioButtonGroup, self).__init__(parent)

        self._model = model 
        self._editor = editor 

        self.button_group = QtWidgets.QButtonGroup(self)

        box = QtWidgets.QGroupBox(label, self)
        lay = QtWidgets.QVBoxLayout(box)
        root = QtWidgets.QVBoxLayout(self)
        root.addWidget(box)

        value = self._editor.get()

        for index in range(self._model.rowCount()):
            item = self._model.item(index)

            button = QtWidgets.QRadioButton(item.text(), self)
            button.setChecked(item.data() == value)
            self.button_group.addButton(button, index)

            lay.addWidget(button)

        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._handle_change)

    def _handle_change(self, button):
        index = self.button_group.id(button)
        item = self._model.item(index)
        self._editor.set(item.data())


class SettingsDialog(QtWidgets.QDialog):
    """Simple dialog for editing settings."""

    def __init__(self, settings):
        """Initialize.

        Args:
            settings (SettingsModel): Settings to edit.
        """

        super(SettingsDialog, self).__init__()

        self._settings = settings 

        self.setWindowTitle('Advanced Settings')

        layout = QtWidgets.QVBoxLayout(self)

        select_color = RadioButtonGroup('Color', self._settings.editor('color'), self.colors(), self)
        checkbox = CheckBox('Checkbox', self._settings.editor('toggle'), self)

        layout.addWidget(select_color)
        layout.addWidget(checkbox)

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
        self._settings.sync()

        super(SettingsDialog, self).accept()


def main():
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(True)

    settings = SettingsModel()
    settings = SettingsModelProxy(settings)

    dialog = SettingsDialog(settings)
    dialog.exec_()

    sys.exit()


if __name__ == '__main__':
    main()
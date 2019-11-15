"""Settings dialog examples.

Each file in the module contains an example of a settings/preferences dialog 
for a tool. The UI/UX of the dialogs is identical. 

The basic dialog uses a straight forward approach with minimal abstraction.

The advanced dialog uses descriptors and a proxy/editor pattern to implement 
smart widgets read/write the values they control, minimizing the boiler plate 
calls to .value() and .getValue() on the QSettings object.
"""
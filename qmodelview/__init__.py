"""Model/View usage examples.

Model/View programming (https://doc.qt.io/qt-5/model-view-programming.html) is a 
method of managing the separation of data persistence from rendering/editing.

This examples will focus on the QStandardItemModel, a generic model for storing 
custom data (https://doc.qt.io/qt-5/qstandarditemmodel.html). For comparison, an
example using an item/widget solution is also presented. The UI/UX of the examples
are identical - a tree of items with status codes, presented with human readable
names. Selecting an item prints the item name and status code.

In my experience, you can do most of your basic UI/IX work - presenting structured 
data, showing icons, managing user selections - with this model and one of the 
built-in views.

Advanced UI/IX work - editing per-item data, custom data rendering, etc - can 
be handled with delegates, which is outside of the scope of thes examples.
"""

__version__ = '1.1.5'
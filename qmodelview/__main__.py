import argparse
import sys 

import common
import item_widget
import model_view 

from PySide2 import QtCore, QtGui, QtWidgets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mv', action='store_true', help='View the Model/View example'
    )

    args = parser.parse_args()

    if args.mv:
        widget = model_view.StatusView
        window_name = 'Model/View'
    else:
        widget = item_widget.StatusWidget
        window_name = 'Item/Widget'

    common.main(widget, window_name)


if __name__ == '__main__':
    main()
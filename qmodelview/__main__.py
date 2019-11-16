import argparse
import sys 

import common
import item_widget
import model_view 
import model_view2 

from PySide2 import QtCore, QtGui, QtWidgets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mv', action='store_true', help='View the Model/View example'
    )
    parser.add_argument(
        '--mv2', action='store_true', help='View the Model/View example'
    )

    args = parser.parse_args()

    if args.mv2:
        model_view2.main()
    elif args.mv:
        model_view.main()
    else:
        item_widget.main()


if __name__ == '__main__':
    main()
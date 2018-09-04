from PyQt5.QtWidgets import (QWidget, QVBoxLayout)
try:
    from . import objecttree
except:
    import objecttree

class ObjectTreeControls(QWidget):

    def __init__(_, parent=None):
        super().__init__(parent)
        _.setWindowTitle('Module / Class / Object explorer')

        objecttree.load_IconSet()
        _.treeWidget = objecttree.ObjectTreeWidget()
        vbox = QVBoxLayout()
        _.setLayout(vbox)
        vbox.addWidget(_.treeWidget)


    def onKeyPressEvent(_,e):
        # for compatibilty calls when external calls + widgets focus
        _.treeWidget.keyPressEvent(e)


if __name__ == '__main__':
    from PyQt5.QtWidgets import (QWidget, QApplication,QMainWindow)
    from testclass import TestClass
    import sys

    class DummyMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

    app = QApplication(sys.argv)
    ex = DummyMainWindow()
    objecttree.load_IconSet()
    obj = TestClass('123')
    otc = ObjectTreeControls()
    otc.treeWidget.addItem('aa', obj)
    otc.show()
    app.exec_()

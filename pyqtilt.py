
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget,
                             QMessageBox,
                             QVBoxLayout, QSplitter)

try :
    from . import GlobalsListWidget
    from . import ObjectTreeControls
except Exception :
    from globalsListWidget import GlobalsListWidget
    from objectTreeControls import ObjectTreeControls

import logging
logger = logging.getLogger("%s" % __name__)


class PyqtiltWidget(QWidget):

    def __init__(_, parent=None):
        super().__init__(parent)
        _.setWindowTitle('Module / Class / Object explorer')
        _.initUI()

    def initUI(_):
        [ logger.info(x) for x in globals()]
        _.globalistwid = GlobalsListWidget(globals())
        # connection between module list and tree is herer
        _.globalistwid.listWidget.itemActivated.connect(_.addObjectToTree)
        _.objtree = ObjectTreeControls(_)
        vbox = QVBoxLayout()
        _.setLayout(vbox)
        vbox.addWidget(_.objtree)
        _.globalistwid.show()
        _.show()

    def addSequencerItem(_, item):
        # insert holder, name as model
        logger.debug('//%s %s' % (str(type(item)), item) )

    def addObjectToTree(_, item):
        _.objtree.treeWidget.addItem(item.name, item.obj)

    def close(_):
        _.globalistwid.close()

    def onKeyPressEvent(_,evt):
        print('ok',evt)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import (QApplication)
    from testclass import TestClass

    app = QApplication(sys.argv)

    A = TestClass(0) # in the current namespace

    b = PyqtiltWidget()
    '''
    b.lerpSelector.show()
    b.lerpSelector.move(300,100)
    b.show()
    b.move(300,300)
    '''
    app.exec_()

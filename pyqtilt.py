
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget,
                             QMessageBox,
                             QHBoxLayout, QSplitter)
#from sequencerDatamodel import SequencerDataModel
#from sequencerTablemodel import SequencerTableModel
#from sequencerTableview import SequencerTableView
# from lerpselector import LerpSelector

try :
    from . import GlobalsListWidget
    from . import ObjectTreeControls
except:
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

        '''
        seqData = SequencerDataModel()
        # XXX can't add a model without a default one...
        seqData.addModel(_,'0')
        seqModel = SequencerTableModel(seqData)
        seqModel.setParent(_) # required message warnings
        seqView = SequencerTableView(seqModel)
        seqView.setModel(seqModel)

        lerpSelector = LerpSelector()
        lerpSelector.c.selected[int].connect(seqView.addFunction)

        _.seqView = seqView
        _.seqData = seqData
        _.seqModel = seqModel
        _.lerpSelector = lerpSelector
        '''
        [ logger.info(x) for x in globals()]
        _.globalistwid = GlobalsListWidget(globals())
        # connection between module list and tree is herer
        _.globalistwid.listWidget.itemActivated.connect(_.addObjectToTree)

        _.objtree = ObjectTreeControls(_)
        '''
        _.objtree.treeWidget.c.activate.connect(_.addSequencerItem)
        _.seqView.c.stop.connect(_.objtree.treeWidget.stopUpdating)
        '''
        hbox = QHBoxLayout()
        splitter1 = QSplitter(Qt.Horizontal)
        _.setLayout(hbox)
        hbox.addWidget(splitter1)

        splitter1.addWidget(_.objtree)
        splitter1.addWidget(seqView)

        _.globalistwid.show()

    def addSequencerItem(_, item):
        # insert holder, name as model
        logger.debug('//%s %s' % (str(type(item)), item) )
        '''
        if _.seqModel.insertModel(item[0], item[1]):
            _.seqView.columnCountChanged(0, 1)
            _.seqView.rowCountChanged(0, 1)
        else:
            QMessageBox.warning(
                _,
                'Hey',
                "This field is already in the sequence",
                QMessageBox.Ok)
        '''

    def addObjectToTree(_, item):
        _.objtree.treeWidget.addItem(item.name, item.obj)
        logger.debug('item added')

    '''
    def addObject(_,name,objtreebj):
        _.objtree.addItem(name,obj)
    '''

    def close(_):
        _.globalistwid.close()

    def onKeyPressEvent(_,evt):
        print('ok',evt)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import (QApplication)
    #import qtfusionstyle

    from testclass import TestClass
    A = TestClass(0)

    app = QApplication(sys.argv)
    #qtfusionstyle.set(app)

    b = PyqtiltWidget()
    '''
    b.lerpSelector.show()
    b.lerpSelector.move(300,100)
    b.show()
    b.move(300,300)
    '''
    app.exec_()


import types
from inspect import isclass

from PyQt5.QtWidgets import (
    QFrame, QWidget,QComboBox,QListWidget,QLabel, QListWidgetItem,QVBoxLayout
)
from PyQt5.QtCore import Qt #, pyqtWrapperType

try:
    from globalsManager import not_classes_or_private
except:
    from .globalsManager import not_classes_or_private

import logging
logger = logging.getLogger("clogger.%s" % __name__)
logger.setLevel(logging.DEBUG)


class ObjectItem(QListWidgetItem):
    '''
    A one-column list
    holding an object displaying it's name and type
    '''

    def __init__(self,name,obj,parentList=None):

        super().__init__(name + '  :: ' + obj.__class__.__name__ ,parentList)
        self.name = name
        self.obj = obj


class GlobalsListWidget(QWidget):


    @classmethod
    def ismainmodule(cls,obj):
        try:
            return obj.__module__ == '__main__'
        except AttributeError:
            return False

        '''
            not name.startswith('__') and
            not name.startswith('GL_') and
            not name.startswith('gl') and
            not name.startswith('PFNGL')
        '''

    def __init__(self, objects):
        super().__init__()
        self.setWindowTitle('modules/namespace')

        listWidget = QListWidget()
        self.listWidget = listWidget
        self.combofilter = QComboBox()

        self.filters = [
            ('__main__', self.ismainmodule),
            ('instances', lambda x: not isclass(x[1]) and
                not isinstance(x[1],types.ModuleType) and
                not isinstance(x[1],types.FunctionType)),
            ('types', lambda x:  type(x[1]) is type),
            #('pyqtwrapper', lambda x:  type(x[1]) is pyqtWrapperType),
            ('customs', lambda x:not (isinstance(x[1],type) or
                                      isinstance(x[1],types.ModuleType) or
                                      isinstance(x[1],types.FunctionType) or
                                      type(x[1]) is int
                                      )),
            ('functions', lambda x:isinstance(x[1],types.FunctionType)),
            ('modules', lambda x:isinstance(x[1],types.ModuleType)),
            ('all', lambda x: True)]

        for x in self.filters : self.combofilter.addItem(x[0])

        self.combofilter.currentIndexChanged.connect(self.filterItems)

        vbox = QVBoxLayout()

        self.setLayout(vbox)
        vbox.addWidget(listWidget)
        vbox.addWidget(self.combofilter)
        label = QLabel(self)
        label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        label.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        vbox.addWidget(label)
        self.label = label
        self.refreshglobals(objects)

        logger.info('Global module list loaded')
        self.resize(300,800)

    def filterItems(self):
        if(self.globs):
            self.listWidget.clear()
            for name,obj in filter(self.filters[self.combofilter.currentIndex()][1],
                                   self.globs):
                if name[:2] != '__':
                    self.listWidget.addItem(ObjectItem(name,obj))
                    self.label.setText("%i / %i modules" % (self.listWidget.count(),len(self.globs)))


    def refreshglobals(self,globs):
        self.listWidget.clear()
        self.globs = globs.items()
        self.label.setText("%i modules" % len(self.globs))

        for name,obj in filter(not_classes_or_private, globs.items()):

            self.listWidget.addItem(ObjectItem(name,obj))
            s = name + ' :: ' + str(type(obj))
            try:
                s = obj.__module__ + '.' + s
            except AttributeError:
                pass

            # logger.debug(s + ' :: ' + str(type(obj)))

        self.listWidget.setSortingEnabled(True)
        self.listWidget.sortItems(Qt.AscendingOrder)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import (QApplication,QWidget)
    from testclass import TestClass
    #from globalsManager import filter_classes_private
    A = TestClass(0)
    app = QApplication(sys.argv)
    globalist = GlobalsListWidget(globals())
    globalist.show()
    app.exec_()

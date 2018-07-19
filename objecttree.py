'''

Pyqtilt
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018/07/18 20:18:53>
Released under the MIT License

ObjectTree

A fully fledged modules/classes/members/functions inspector

function can be called by double clicking them or by pressing enter.

Arguments and members are editable.

activating the __init__ method of a class brings a new instance into the tree

Since tuple are immutable, editing a tuple overwrites the entire previous one

The inspection will detect methods with invalid signatures,
so far, only initializer lacking a self parameter
(the underscore symbol in my book).

arrays can be rewritten as long as the keep the same size
(an update upon keypress is needed)

Numbers can be modified by using a contextual slider.
This slider has to be improved for floating value modification
(using a shift key for instance) that slider could also turn invisible.

'''

import ast, types, sys, time
from inspect import signature, getmembers, isclass, ismethod, _empty

import numpy # for type recognition / exclusion

from threading import Thread # keep the tree updated when data change


from os import path
from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt5.QtGui import QIcon, QBrush, QMouseEvent
from PyQt5.QtWidgets import (
    QTreeWidget,QTreeWidgetItem, QItemDelegate, QStyledItemDelegate,
    QAction, qApp, QMenu, QSlider, QInputDialog
)
import debuglog
log = debuglog.get(__name__)

'''
import log
log = logging.getlog(__name__)
log.setLevel(logging.DEBUG)
'''
icons_path = 'icons'
iconDict = None

# types we won't dig into :
_skippedTypes = [numpy.number, numpy.ndarray] # [... numpy.uint32, numpy.float64, numpy.ndarray ]
skipped = {}
def skip(*args): pass
debug = skip
# debug = print
# max member depth
MAXLEVEL = 5

try:
    from . import pyqtilt_rc
except:
    import pyqtilt_rc


def main():
    import debuglog
    log = debuglog.get('objtree')
    from testclass import TestClass
    from PyQt5.QtWidgets import QMainWindow, QApplication


    class DummyMainWindow(QMainWindow):

        def __init__(_):
            super().__init__()
            _.initUI()


        def initUI(_):
            exitAction = QAction(QIcon('exit.png'), '&Exit', _)
            exitAction.setShortcut('Ctrl+Q')
            exitAction.setStatusTip('Exit application')
            exitAction.triggered.connect(qApp.quit)

            _.statusBar()

            menubar = _.menuBar()
            fileMenu = menubar.addMenu('&File')
            fileMenu.addAction(exitAction)
            _.setGeometry(300, 300, 300, 200)
            _.setWindowTitle('Module / Class / Object explorer')
            _.show()

    app = QApplication(sys.argv)
    ex = DummyMainWindow()
    ex.show()

    load_IconSet()

    # goes in the ctor

    obj1 = TestClass('x')
    obj2 = obj1
    # slight problem with module, some object don't have a holder
    m = __import__('testclass')
    treeWidget = ObjectTreeWidget()
    treeWidget.addItem('A', obj1)
    treeWidget.addItem('A_instance2', obj2)
    treeWidget.addItem('module', m)
    treeWidget.move(400, 200)
    #treeWidget.header().resizeSection(0, treeWidget.width()/2)
    treeWidget.resize(900, 600)
    ex.setCentralWidget(treeWidget)

    app.exec_()
    print('running')
    app.closeAllWindows()




def load_IconSet():
    global iconDict
    iconDict = {
        'string':   QIcon(':/images/string.png'),
        'on'    :   QIcon(':/images/ToggleOn-32.png'),
        'off'   :   QIcon(':/images/ToggleOff-32.png'),
        'wheels':   QIcon(':/images/wheel.gif'),
        'tuple' :   QIcon(':/images/tuple.gif'),
        'list'  :   QIcon(':/images/list.gif'),
        'type'  :   QIcon(':/images/type.png'),
        'locked':   QIcon(':/images/locked.png')
    }


def GetSubList(obj):

    if isclass(type(obj)):
        if type(obj) is list or type(obj) is tuple:
            # set the name as the indice in the list
            # i stays as integer for holder[i] access
            members = [(i, o) for i, o in enumerate(obj)]
            return members

        else:
            try:
                members = getmembers(
                    obj, lambda x: not isinstance(x, types.ModuleType))
                # discardedFields = [ '__builtins__','__cached__','__doc__','__file__','__loader__','__name__','__package__','__spec__']
                # __dict__,__dir__,__eq__,__format__,__ge__,__getattribute__,__gt__,__hash__,__init__,__le__,__lt__,__module__,__ne__,__new__,__reduce__,__reduce_ex__,__repr__,__setattr__,__sizeof__,__str__,__subclasshook__,__weakref__
                #print(type(members))
                #[ log.debug(x + ' ' + str(o)) for(x,o) in members]
                #[ print(x + ' ' + str(o)) for(x,o) in members]
                members = [(name, o)
                           for (name, o) in members if not name.startswith('__')
                           ]
                members.append(('__init__', obj.__init__))

                #members.append()
                return members
            except Exception as e:
                log.exception(e)

    return []

def local_exec(a):
    ldict = globals()
    try:
        exec("a=%s" % a, globals(), ldict)
        a = ldict['a']
        print(a)
        return a

    except Exception as e:
        print(ldict)
        print(e)

# xxx unused
class ItemDelegate(QItemDelegate):

    def __init__(_, contextMenu, parent):
        super().__init__(parent)
        _.contextMenu = contextMenu

    # other event emitter might try to call this without the right arguments
    def event(_, event):
        print('item delegate event',event)
        return True

    def event1(_, event, model=None, option=None, index=None):
        if not model:
            return True
        print(model, type(model.data(index)))
        print('rightbut')
        item = model.data(index)
        if event.type() == QEvent.MouseButtonPress and index.isValid():
            mouseEvent = QMouseEvent(event)
            if mouseEvent:
                if mouseEvent.button() == Qt.RightButton:
                    print('rightbut')

                    _.contextMenu.exec(
                        _.contextMenu.mapToGlobal(mouseEvent.pos())
                    )

                    if type(item) is FunctionItem:
                        item.perform_call()
                    return True
        return False


class Communicate(QObject):
    activate = pyqtSignal(object)


class ObjectTreeWidget(QTreeWidget):

    ''' A TreeWidget designed to explore, read and control python objects
        - the keypress / fire function event
        - generic python subtypes items
        - can activate the functions of the explored object and create new instance.
    '''

    def __init__(_, parent=None):
        ''' initialize an empty obtree '''
        QTreeWidget.__init__(_, parent)
        _.setWindowTitle('Module / Class / Object explorer')
        if not iconDict: load_IconSet()
        _.c = Communicate()
        _._ids = []
        _.setColumnCount(2)

        _.expandToDepth(1)

        _.setSortingEnabled(True)
        _.sortItems(0, Qt.AscendingOrder)

        #_.itemDoubleClicked.connect(_.dblClickItem)

        _.itemChanged.connect(_.itemChange)
        # set column 0 as non editable
        _.setHeaderLabels(['Object', 'value/signature'])
        _.updating = False  # for contiuous update if change occurs from outside to the model
        _.indexTop = _.model().index(0, 0)

        _.contextMenu = QMenu("Chain menu", _)
        action_chain = QAction("chain", _)
        action_chain.triggered.connect(_.itemChain)
        _.contextMenu.addAction(action_chain)

        _.contextMenuFunc = QMenu("Function menu", _)
        action_execute = QAction("execute", _)
        action_execute.triggered.connect(_.itemActivation)
        _.contextMenuFunc.addAction(action_execute)

        _.intSlider = QSlider(Qt.Horizontal)
        _.intSlider.setWindowFlags( Qt.FramelessWindowHint)

        _.intSlider.sliderMoved.connect(_.sliderMoved)

        _.intSlider.sliderMoved.connect(_.sliderMoved)
        _.intSlider.installEventFilter(_)
        _.setContextMenuPolicy(Qt.CustomContextMenu)
        _.customContextMenuRequested.connect(_.showContextMenu)
        #_.setItemDelegateForColumn(0, NoEditDelegate(_))
        _.setItemDelegateForColumn(0, ItemDelegate(_.contextMenu,_))
        _.setItemDelegate(ItemDelegate(_.contextMenu,_)) # XXX ctx menu required ??
        _.setFocusPolicy(Qt.ClickFocus)


    def updateNamespace(ns,object):
        ''' insert the object into that global namespace
            be carefull with collisions.
        '''
        globals().update(ns)


    def bdf(_, parent, obj, level=0):
        ''' recurse the object structure and populate the tree
            keep a hash of objects met to prevent looping
            This function belongs to the ObjectTreeWidget
            for bookkeeping the hash list

            XXX : a label for the dup object could be good,
                  pressing the label would jump to the original object
            XXX : todo solve this different id story for functions
        '''
        if level > MAXLEVEL : return

        sublevel = []

        if True in [isinstance(obj,x) for x in _skippedTypes]:
            # avoid full print of ndarrays
            T = type(obj)
            sys.stdout.write(".")
            #print(level*' '+"└" ,T, "skipped")
            x = skipped.get(T) or 0
            x += 1
            skipped[T] = x
            return

        #print(level*' '+"╚",obj, type(obj))
        debug(level*' '+"└", type(obj))

        # display members
        for name, o in GetSubList(obj):
            # ----- output the tree in the console
            debug(level*' '+"├",name, type(o), id(o), ' : ', id(obj))

            # will hardly log big objects with the rainbow log
            #log.debug(level*' '+" ┣ %s %s %s" % (name,str(obj),id(obj)))
            #log.debug(" ┣ %s %s %s" % (name,str(obj),id(obj)))


            # todo  : optimize out the test order
            if type(o) not in (int, bool, float, str) and id(o) in _._ids:
                # need to add a référence item
                log.warning('already in : %s %s (%i ids)' % (name, type(o), len(_._ids)))
                #print('already in : %s %s' % (name, type(o)))
                continue
            else:  # léger risque de leak sur cette sauvegarde
                _._ids.append(id(o))
                # item = ReferenceItem() #XXX todo : add the id in the items
                # search for the item holding id
                # set in as
                # item = ReferenceItem(it)

            if name == '__init__':
                item = FunctionItem(parent, name,  o)

            # primitives types. They need a holder
            elif type(o) is bool:  # isinstance(o,bool):
                item = BooleanItem(parent, obj, name, o)
            elif type(o) is int:  # isinstance(o,int) or isinstance(o,float):
                item = IntItem(parent, obj, name, o)
            elif type(o) is float:  # isinstance(o,float) :
                item = FloatItem(parent, obj, name, o)
            elif type(o) is str:  # isinstance(o,str):
                item = StrItem(parent, obj, name, o)

            # compound types. holds it_

            elif ismethod(o):
                item = FunctionItem(parent, name, o)
            elif type(o) is list:  # isinstance(o,list):
                item = ListItem(parent, name, o)
                sublevel.append((item, o))
            elif isinstance(o, tuple):
                # setting the tuple set a new whole tuple
                item = TupleItem(parent, name, o)
                sublevel.append((item, o))
            elif isinstance(o,type): # a class !
                item = TypeItem(parent, name, o)
                sublevel.append((item, o))

            # at module level
            # elif isinstance(obj, types.FunctionType):
            #    item = FunctionItem(parent, o, name,obj)

            # this is only to discard functions, builtins and modules
            # but this should already be filtered by getSubList
            elif isclass(type(o)):
                try:
                    item = TreeItem(parent, obj, name,  [str(name), o.__class__.__name__])
                    item.setFlags(
                        Qt.ItemIsEditable |
                        Qt.ItemIsSelectable |
                        Qt.ItemIsEnabled)
                    sublevel.append((item, o))

                except Exception as e:
                    print(e)
                    print(obj,name)


        # then dig the object, recurse parent widget, object, name
        for parent, obj in sublevel:
            _.bdf(parent, obj, level+1)


    def eventFilter(_,obj, event):
        if (event.type() == QEvent.FocusOut) :
            _.intSlider.close()
            return True
        else :
            return QObject.eventFilter(_,obj, event)


    def sliderMoved(_,value):
        print(value)


    def showContextMenu(_, pos):
        item = _.currentItem()
        column = _.currentIndex().column()

        if column == 0:
            # XXX todo :
            print(type(item))
            if type(item) is FunctionItem :
                _.contextMenuFunc.exec(_.mapToGlobal(pos))

            _.contextMenu.exec(_.mapToGlobal(pos))
        elif column == 1:
            if type(item) is FunctionItem :
                _.contextMenuFunc.exec(_.mapToGlobal(pos))
            elif type(item) is IntItem or type(item) is FloatItem:

                v = item.holder[item.name]
                _.intSlider.setRange(-abs(v*2+5), abs(v*2+10))

                _.intSlider.move(_.mapToGlobal(pos))
                _.intSlider.setFocus()
                _.intSlider.setValue(item.holder[item.name])
                _.intSlider.show()
                _.intSlider.raise_()



    def itemChain(_):
        it = _.selectedItems()
        if not it : return
        has = it[0]
        chain = []
        if type(has) is ParameterItem: # xxx todo : an event filter
            return None
        while has:
            parent = has.parent()
            if not parent:
                chain.append(has.name)
                break
            else:
                if type(parent) is ListItem or type(parent) is TupleItem:
                    chain.append('[%s]' % str(has.name))
                    # intItem are ints for holder access holder[x]
                else:
                    chain.append('.%s' % str(has.name))
                    # intItem are ints for holder access holder[x]

            has = parent

        s = ''.join(chain[::-1])
        print(s)
        # evaluate the name in the global namespace (updated by _.addItem)
        ldict = {}
        try:
            exec("x=%s" % s, globals(), ldict)
            o = ldict['x']

            #if type(o) in (int, bool, float, str):
            # a primitive type. we need a handle.
            print('#', s,o, type(o))
            if isinstance(o,types.ModuleType):
                print(o.__file__)
            log.debug('%s %s' % (s,o))
            return chain.reverse()

        except Exception as e:
            log.exception(e)
            return None


    def itemActivation(_):
        if not _.selectedItems() :
            return
        item = _.selectedItems()[0]
        _.activateItem(item)

    def sliderMoved(_):
        item = _.selectedItems()[0]
        if _.intSlider.value() < _.intSlider.minimum()+1:
            _.intSlider.setRange(_.intSlider.minimum()-5, _.intSlider.maximum())

        # xxx won't work on a tuple !
        item.holder[item.name] = _.intSlider.value()
        #indexEnd = _.model().index(1, _.model().rowCount())
        _.dataChanged(_.currentIndex(), _.currentIndex(), [Qt.DisplayRole])
        #_.update()

    def startUpdating(_):
        _.updating = True
        # _.blockSignals(True)
        Thread(target=_.updateData).start()

    def updateData(_):
        while _.updating:
            indexEnd = _.model().index(1, _.model().rowCount())
            _.dataChanged(_.indexTop, indexEnd, [Qt.DisplayRole])
            _.update()
            time.sleep(0.1)
        # _.blockSignals(False)

    def stopUpdating(_):
        _.updating = False
        print('updating stopped')

    def clear(_):
        for i in range(_.topLevelItemCount()):
            _.takeTopLevelItem(i)
        _._ids.clear()

    def addItem(_, name, obj, user=False):

        globals().update({name:obj})

        # _.addTopLevelItems(rootsItem)
        it = ObjectItem(_.invisibleRootItem(), name, obj)
        _.bdf(it, obj, level=0)
        if user:
            # new instances
            print('user created')
            it.bg = QBrush(Qt.green)

        if skipped: log.info('skipped %s' % skipped)
        print('skipped:',skipped)

    def itemChange(_, item, column):
        return
        if type(item) is BooleanItem:
            item.holder[item.name] = True if item.checkState(
                1) == Qt.Checked else False
            item.setIcon(0, item.onIcon if item.checkState(
                1) == Qt.Checked
                else item.offIcon)

    def keyPressEvent(_, event):
        print(__name__,'keypress')
        try:

            if event.key() == Qt.Key_Return:
                if not _.selectedItems() : return
                item = _.selectedItems()[0]
                # the ItemDelegate will handle this. (there's no item.editing so far.)
                if item.editing: return
                else:
                    _.activateItem(item)
                    print('activated')
        except TypeError as te:
            log.error(te)

        #QTreeView.keyPressEvent(_, event)

    def activateItem(_, item):
        '''
        si c'est un type primitif, ajoute la référence
        dans le séquenceur
        si c'est un paramètre de fonction, ajoute la fonction
        avec l'appel f(x,a) ou a les valeurs courante du paramètre
        il faut un moyen d'appeler des fonctions sur les listes
        du séquenceur.
        '''
        log.debug('activating')
        print('?',item, type(item), item.o, type(item.o))
        if type(item) is FunctionItem:
            x = item.perform_call()
            log.debug(x) # XXX put in a result stack
        else:
            if isinstance(item, PrimitiveTypeItem) or type(item) is BooleanItem:
                try:
                    log.debug([
                        item.name, type(item.o), item.o,
                        item.holder[item.name], id(item.holder)])
                    #if type(item) is BooleanItem:
                    #    item.tr

                except KeyError as e:
                    print(e)
                    log.error(e)
                try:
                    print('emit')
                    _.c.activate.emit((item.holder, item.name))
                except Exception as e:
                    log.error(e)

            if isinstance(item, TypeItem):
                #if type(item) is
                print('what to do',item.o, type(item.o))
                try:
                    text, ok = QInputDialog.getText(_, 'Input Dialog', 'instance name:')
                    if ok:
                        _.addItem(str(text),item.o())

                except Exception as e :
                    log.error(e)

                # ObjectFactory.construct(item.o)

            else:
                try :
                    print('? what to do with '+item.name, ' ', item.o, item.holder[item.name])
                except Exception as e :
                    log.error(e)

    # filter mouse right/left
    '''
    def dblClickItem(_, item, column):
        if column == 0:
            _.activateItem(item)
    '''

    def rightClickItem(_,item,column):
        print('??')
        _.showContextMenu()
        if column == 0 and type(item) is FunctionItem :
            item.perform_call()


class NoEditDelegate(QStyledItemDelegate):

    def __init__(_, parent):
        QStyledItemDelegate.__init__(_, parent)

    def createEditor(_, parent, optionViewItem, index):
        return None
# http://stackoverflow.com/questions/2801959/making-only-one-column-of-a-qtreewidgetitem-editable


selectable_editable_enabled = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled


class TreeItem(QTreeWidgetItem):

    def __init__(_, parent, o, name,  strings):
        ''' holder is required for primitive types,
        otherwise we end handling the value, not the reference '''
        super().__init__(parent, strings)
        _.o = o
        _.name = name
        # XXX find a way to prevent the enter keyboard when editing
        # to add to the sequencer
        _.editing = False

    def __lt__(_, other):
        ''' comparator < for sorting '''
        if _.childCount() > 0:
            if other.childCount == 0:
                return False
        else:
            if other.childCount() > 0:
                return True

        return _.text(0) < other.text(0)


    def setData(_,column, role, value):
        super().setData(column, role, value)
        _.treeWidget().itemChanged.emit(_.parent(),column)
        print('sat')



class BooleanItem(TreeItem):

    def __init__(_, parent, holder, name,   b):
        super().__init__(parent, id(b), name,   [name])

        try:
            _.holder = holder.__dict__
        except AttributeError as e:
            log.exception(e)
        _.onIcon = iconDict['on']
        _.offIcon = iconDict['off']
        _.setFlags(Qt.ItemIsUserCheckable |
                    Qt.ItemIsSelectable |
                    Qt.ItemIsEnabled)
        _.setCheckState(1, Qt.Checked if b else Qt.Unchecked)
        _.setIcon(0, _.onIcon if b else _.offIcon)


    def setData(_,column, role, value):
        super().setData(column, role, value)
        if role == Qt.CheckStateRole:
            try:
                _.holder[_.name] = True if value else False
            except TypeError as te:
                log.exception(te)
            try:
                _.setIcon(0, _.onIcon if _.holder[_.name] else _.offIcon)
            except KeyError as ke:
                log.exception(ke)


skipped = {}

class PrimitiveTypeItem(TreeItem):
    ''' a node holding the parent object in order to perform the value set '''

    def __init__(_, parent, holder, name,   p):
        '''
        object are adressed by o.__dict__[name]
        list by : l[name] where name is the indice
        federate affectation of var n turns to holder[name] = x
        '''
        try:
            if type(holder) in [list,tuple]:
                _.holder = holder
            else:
                _.holder = holder.__dict__
        except AttributeError:
            try:
                # type(holder) in [memoryview, numpy.uint32, numpy.dtype,]:
                # list goes on for all ctypes without __dict__ but a __getitem__
                if type(holder) in [numpy.uint32, numpy.dtype]:
                    x = skipped.get(name) or 0
                    x += 1
                    skipped[name] = x
                    print("skipped %s %s" % ( name, type(holder)))
                else:
                    _.holder = holder
            except AttributeError:
                print('no holder at this item : %s (%s)' % ( name, type(holder)))

        super().__init__(parent, p, name,   [str(name), str(p)])
        _.setFlags(selectable_editable_enabled)

    def data(_, column, role):

        if role == Qt.DisplayRole:
            _.editing = False
            if column == 0:
                return _.name
            elif column == 1:
                try:
                    return _.holder[_.name]
                except KeyError:
                    return '???'

        if role == Qt.EditRole:
            _.editing = True
            if column == 0:
                return _.name
            elif column == 1:
                try:
                    return _.holder[_.name]
                except KeyError:
                    return '---'


    def setData(_, column, role, value):
        if role == Qt.EditRole and column == 1:
            print('setting...')
            _.editing = False
            try:
                _.holder[_.name] = value
            except Exception as e:
                log.error(e)
                print(e)

class IntItem(PrimitiveTypeItem):

    def __init__(_, parent, holder, name,  i):
        super().__init__(parent, holder, name,  i)


class StrItem(PrimitiveTypeItem):

    def __init__(_, parent, holder, name,   s):
        super().__init__(parent, holder, name,   s)
        _._icon = iconDict['string']

    def data(_, column, role):
        if role == Qt.DecorationRole and column == 0:
            return _._icon
        else:
            return super(StrItem, _).data(column, role)


# XXX todo : the floating point representation with , and . is moot. stick to point '.'
# so we can copy paste the value in our codes
class FloatItem(PrimitiveTypeItem):

    def __init__(_, parent, holder, name,  i):
        super().__init__(parent, holder, name,  i)


class FunctionItem(TreeItem):
    ''' checkable will make the variator/value changed synchronized
        XXX subclass

        The children are all ParameterItems
    '''

    def __init__(_, parent, name,  f):
        # functions of a same object seems unlikely to share id XXX
        # when sub'ed (the holder object is passed as argument)
        # if a=A();b(a) a.f and b.a.f ids are differents
        # perhaps either the callee is different
        super().__init__(parent, f, name, [str(name), str(f)])
        _.func = f  # == _.o
        try:
            sig = signature(f)
            _.signature = sig
            _.setFlags(Qt.ItemIsUserCheckable | selectable_editable_enabled)
            _._icon = iconDict['wheels']

            # print(sig.parameters, type(sig.parameters), sig.parameters.values())
            if len(sig.parameters.keys()):
                for k in sig.parameters.keys():
                    #log.debug('default %s' % sig.parameters[k].default)
                    defaultParam = sig.parameters[k].default
                    if defaultParam == _empty:
                        defaultParam = None
                    ParameterItem(_, k, defaultParam)
        except ValueError as ve:
            print(ve)
            print('error on %s' % name)
            # log.error('on %s' % name)
            log.exception(ve)

    def data(_, column, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == 0:
                return _.name
            elif column == 1:
                v = []
                for i in range(_.childCount()):
                    v.append(str(_.child(i).value))
                return ','.join(v)  # or str(_.signature)
        elif role == Qt.DecorationRole and column == 0:
            return _._icon

    '''
    extra feature : edit/call by writing into the inline parameter
    would require parsing, validating number of arguments, keypress handling, etc..
    def setData(_,column, role, value):
        # call the function upon validation
        if role == Qt.EditRole and column == 1:
            args = str.split(value,',')
            for i,a in enumerate(args):
                _.child(i).value = a
    '''

    def perform_call(_):
        ''' gather children values XXX default parameters ?'''
        params = []
        for i in range(_.childCount()):
            v = _.child(i).value
            if not v or v == '':
                v = _.child(i).default
            params.append(v)  # == let defaut valuue (!= None)
        args = tuple(params)

        try:
            log.debug('call')
            if _.name == '__init__' :
                print('init', _.parent().o, _.func)
                x = _.parent().o.__new__(_.parent().o, *args)
                x.__init__(*args[1:])
                text, ok = QInputDialog.getText(None, 'Input Dialog', 'instance name:')
                if ok:
                    _.treeWidget().addItem(str(text),x,user=True)

            else:
                x = _.func(*args)
            log.debug(x)

            return(x)
            #return _.func(*args)
        except TypeError as e:
            log.debug(e)


class ParameterItem(TreeItem):
    # parameters item have no id as they are very
    # unlikely to lose couple with their fonction

    def __init__(_, parent, name,  default=None):
        super().__init__(parent, None, name, [name])
        _.parent = parent
        _.value = default
        _.default = default
        _.setFlags(selectable_editable_enabled)

    def data(_, column, role):
        if role == Qt.DisplayRole:
            if column == 0:
                return _.name
            elif column == 1:
                return _.value

    def setData(_, column, role, value):
        ''' the parent is a FunctionItem
            gather children values, perform call '''
        if role == Qt.EditRole and column == 1:
            _.value = value
            # but don't perform_call()
        else:
            pass


class ListItem(TreeItem):

    def __init__(_, parent, name,  o):
        # the name of the list can be a number it belongs to list (as for any
        # other object)
        super().__init__(parent, o, name, [str(name), str(o)])  # dup with set data
        _.setFlags(selectable_editable_enabled)
        _._icon = iconDict['list']

        # for e in li:
        #    _.treeWidget().bdf(_,e)

    def data(_, column, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == 0:
                return _.name
            elif column == 1:
                return str(_.o)  # or _.text()
        elif role == Qt.DecorationRole and column == 0:
            return _._icon

    def setData(_, column, role, value):
        if role == Qt.EditRole and column == 1:
            try:
                li = ast.literal_eval(value)
                # attributing a list create a new object.
                # if we give this list to _.i, this would 'detach' the children
                # wich still have their previous holder
                # since this a literal evaluation, any kind of object may be happended
                # to the list, which complicate a bit the logic.
                # on may assume that the type of items must not change
                # and that we are manipulating a template list, not a generic
                # one

                ''' if the list size has change
                dl = len(li) - len(_.o)
                if dl > 0 :
                    childli = []
                '''
                if len(li) == len(_.o):
                    for i, x in enumerate(li):
                        _.o[i] = x

                print(">>", type(_.o), id(_.o))
                # if the parent is a list item, update it's view as well
                for x in range(len(_.o)):
                    print(_.child(x))
                    #_.child(x).o = _.o[x]
                    _.child(x).emitDataChanged()
                # for x in range(_.childCount()):
                #    _.child(x).emitDataChanged()

            except SyntaxError:
                pass
            except ValueError:
                pass


class TupleItem(TreeItem):

    def __init__(_, parent, name,  o):
        # the name of the object is its indice if it belongs
        # to list, a tuple, a set or other kind of arrays
        # (as for any other object)

        super().__init__(parent, o, name,  [str(name), str(o)])  # dup with set data
        _.setFlags(selectable_editable_enabled)
        _._icon = iconDict['list']

        # for e in li:
        #    _.treeWidget().bdf(_,e)

    def data(_, column, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == 0:
                return _.name
            elif column == 1:
                return str(_.o)  # or _.text()
        elif role == Qt.DecorationRole and column == 0:
            return _._icon

    def setData(_, column, role, value):
        # tuple are immutable.
        # this push a new tuple into the holder object

        if role == Qt.EditRole and column == 1:
            try:
                li = ast.literal_eval(value)
                # attributing a tuple create a new object.
                _.o = li

                print(">>", type(_.o), id(_.o))

                for i, x in enumerate(_.o):
                    log.debug(_.child(i))
                    _.child(i).holder = _.o
                    _.child(i).o = x
                    #_.child(x).o = _.o[x]
                    _.child(i).emitDataChanged()
                # for x in range(_.childCount()):
                #    _.child(x).emitDataChanged()

            except SyntaxError:
                pass
            except ValueError:
                pass


class ObjectItem(TreeItem):

    def __init__(_, parent, name,  o):
        super().__init__(parent, o, name,  [str(name), str(type(o))])  # dup set data
        _.setFlags(selectable_editable_enabled)
        _.setBackground(0,QBrush(Qt.red))
        _.bg = QBrush(Qt.transparent)


    def data(_, column, role):
        if role == Qt.DisplayRole:
            return _.name
        if role == Qt.BackgroundRole:
            #return Qt.red
            return _.bg


    def setData(_, column, role, value):

        if role == Qt.EditRole:
            # simply eval the right col if it's a list comprising only
            # primitive type
            #
            # otherwise expand
            #

            pass


class TypeItem(TreeItem):

    def __init__(_, parent, name,  o):
        _._icon = iconDict['type']
        super().__init__(parent, o, name,  [str(name), str(type(o))])


    def setData(_, column, role, value):
        if role == Qt.EditRole: # xxx yes ?
            pass


class LockedItem(TreeItem):
    ''' items we don't want to explore further (indexedbuffer for instance)'''
    def __init__(_, parent, name,  o):
        _._icon = iconDict['locked']
        super().__init__(parent, o, name,  [name, str(type(o))])  # dup with set data


    def setData(_, column, role, value):
        if role == Qt.EditRole:

            pass



'''
def onTreeWidgetItemDoubleClicked(index):
    print (index.column(), isEditable(index.column()))
    item = treeWidget.itemFromIndex(index)
    flags = item.flags()
    print ('>>', int(flags | Qt.ItemIsEditable) )
    if isEditable(index.column()):
        item.setFlags(flags | Qt.ItemIsEditable)
        #treeWidget.editItem(item, index.column())
    else:
        item.setFlags(flags ^ Qt.ItemIsEditable)
'''

# XXX todo : search the tree

'''
def dfs(term):
    pass

def bfs(term):
    pass
'''

if __name__ == '__main__':
    main()


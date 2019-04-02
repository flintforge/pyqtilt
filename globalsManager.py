
''' may turn out generic
hence specific class '''
import types
#from PyQt5.QtCore import pyqtWrapperType

def filter_classes_private(items):
    ''' discard classes, builtins and privates '''
    return [(name,obj) for name,obj in items.items()
                if not name.startswith('__') and
                    #not name.startwith()
                    #not isinstance(obj, type)
                    not type(obj) is type
            ]


def not_classes_or_private(obj):
    name,obj = obj[0],obj[1]
    ''' discard classes, builtins and privates '''
    return (
        not isinstance(obj,types.ModuleType) and
        # not isinstance(obj, type)
        # not type(obj) is type and
        # not type(obj) is pyqtWrapperType and
        not isinstance(obj, types.FunctionType) and
        not name.startswith('__') and
        not name.startswith('GL_') and
        not name.startswith('gl') and
        not name.startswith('PFNGL')

    )

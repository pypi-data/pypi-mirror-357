#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Mixins to use for composing type shapes.

"""

from .ControlFlowDescriptions import (
    ControlFlowDescriptionAddUnsupported,
    ControlFlowDescriptionElementBasedEscape,
    ControlFlowDescriptionNoEscape,
    ControlFlowDescriptionSubUnsupported,
)
from .StandardShapes import tshape_unknown


class ShapeContainerMixin(object):
    """Mixin that defines the common container shape functions."""

    # Mixins are required to define empty slots
    __slots__ = ()

    @staticmethod
    def hasShapeSlotBool():
        return True

    @staticmethod
    def hasShapeSlotLen():
        return True

    @staticmethod
    def hasShapeSlotContains():
        return True

    @staticmethod
    def hasShapeSlotIter():
        return True

    @staticmethod
    def hasShapeSlotNext():
        return False

    @staticmethod
    def hasShapeModule():
        return False

    @staticmethod
    def getOperationUnaryReprEscape():
        return ControlFlowDescriptionElementBasedEscape

    @staticmethod
    def hasShapeTrustedAttributes():
        return True


class ShapeContainerMutableMixin(ShapeContainerMixin):
    # Mixins are required to define empty slots
    __slots__ = ()

    @staticmethod
    def hasShapeSlotHash():
        return False


class ShapeContainerImmutableMixin(ShapeContainerMixin):
    # Mixins are required to define empty slots
    __slots__ = ()

    @staticmethod
    def hasShapeSlotHash():
        return True


class ShapeNotContainerMixin(object):
    # Mixins are required to define empty slots
    __slots__ = ()

    @staticmethod
    def hasShapeSlotBool():
        return True

    @staticmethod
    def hasShapeSlotLen():
        return False

    @staticmethod
    def hasShapeSlotIter():
        return False

    @staticmethod
    def hasShapeSlotNext():
        return False

    @staticmethod
    def hasShapeSlotContains():
        return False

    @staticmethod
    def hasShapeModule():
        return False

    @staticmethod
    def getOperationUnaryReprEscape():
        return ControlFlowDescriptionNoEscape


class ShapeNotNumberMixin(object):
    """Mixin that defines the number slots to be set."""

    # Mixins are required to define empty slots
    __slots__ = ()

    @staticmethod
    def hasShapeSlotBool():
        return True

    @staticmethod
    def hasShapeSlotAbs():
        return False

    @staticmethod
    def hasShapeSlotInt():
        return False

    @staticmethod
    def hasShapeSlotLong():
        return False

    @staticmethod
    def hasShapeSlotFloat():
        return False

    @staticmethod
    def hasShapeSlotComplex():
        return False

    # TODO: Seems misplaced
    @staticmethod
    def hasShapeModule():
        return False

    @staticmethod
    def getOperationUnaryAddShape():
        return tshape_unknown, ControlFlowDescriptionAddUnsupported

    @staticmethod
    def getOperationUnarySubShape():
        return tshape_unknown, ControlFlowDescriptionSubUnsupported


class ShapeNumberMixin(object):
    """Mixin that defines the number slots to be set."""

    # Mixins are required to define empty slots
    __slots__ = ()

    @staticmethod
    def hasShapeSlotBool():
        return True

    @staticmethod
    def hasShapeSlotAbs():
        return True

    @staticmethod
    def hasShapeSlotInt():
        return True

    @staticmethod
    def hasShapeSlotLong():
        return True

    @staticmethod
    def hasShapeSlotFloat():
        return True

    @staticmethod
    def hasShapeSlotComplex():
        return True

    @staticmethod
    def hasShapeSlotHash():
        return True

    @staticmethod
    def hasShapeModule():
        return False

    @staticmethod
    def hasShapeTrustedAttributes():
        return True

    @staticmethod
    def getOperationUnaryReprEscape():
        return ControlFlowDescriptionNoEscape

    def getOperationUnaryAddShape(self):
        return self, ControlFlowDescriptionNoEscape

    def getOperationUnarySubShape(self):
        return self, ControlFlowDescriptionNoEscape


class ShapeIteratorMixin(ShapeNotContainerMixin):
    # Mixins are required to define empty slots
    __slots__ = ()

    @staticmethod
    def isShapeIterator():
        return True

    @staticmethod
    def getIteratedShape():
        return None

    @staticmethod
    def hasShapeSlotIter():
        return True

    @staticmethod
    def hasShapeSlotNext():
        return True

    @staticmethod
    def hasShapeSlotNextCode():
        """Does next execute code, i.e. control flow escaped.

        For most known iterators that is not the case, only the generic
        tshape_iterator needs to say "do not know", aka None.
        """
        return False

    @staticmethod
    def hasShapeSlotContains():
        return True

    @staticmethod
    def hasShapeSlotHash():
        return True




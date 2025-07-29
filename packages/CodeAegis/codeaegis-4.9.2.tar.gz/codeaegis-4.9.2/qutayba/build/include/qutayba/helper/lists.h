//     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file

#ifndef __DEVILPY_HELPER_LISTS_H__
#define __DEVILPY_HELPER_LISTS_H__

// Like PyList_SET_ITEM but takes a reference to the item.
#define PyList_SET_ITEM0(tuple, index, value)                                                                          \
    {                                                                                                                  \
        PyObject *tmp = value;                                                                                         \
        Py_INCREF(tmp);                                                                                                \
        PyList_SET_ITEM(tuple, index, tmp);                                                                            \
    }

#ifndef _PyList_ITEMS
#define _PyList_ITEMS(op) (((PyListObject *)(op))->ob_item)
#endif

#if PYTHON_VERSION >= 0x3a0
#define DEVILPY_LIST_HAS_FREELIST 1
extern PyObject *MAKE_LIST_EMPTY(PyThreadState *tstate, Py_ssize_t size);
#else
#define DEVILPY_LIST_HAS_FREELIST 0

#define MAKE_LIST_EMPTY(tstate, size) PyList_New(size)
#endif

extern bool LIST_EXTEND_FROM_ITERABLE(PyThreadState *tstate, PyObject *list, PyObject *other);
extern bool LIST_EXTEND_FOR_UNPACK(PyThreadState *tstate, PyObject *list, PyObject *other);

// Like "PyList_Append", but we get to specify the transfer of refcount ownership.
extern bool LIST_APPEND1(PyObject *target, PyObject *item);
extern bool LIST_APPEND0(PyObject *target, PyObject *item);

// Like "list.remove"
bool LIST_REMOVE(PyObject *target, PyObject *item);

// Like list.clear
extern void LIST_CLEAR(PyObject *target);

// Like list.reverse
extern void LIST_REVERSE(PyObject *list);

// Like list.copy
extern PyObject *LIST_COPY(PyThreadState *tstate, PyObject *list);

// Like list.count
extern PyObject *LIST_COUNT(PyObject *list, PyObject *item);

// Like list.index
extern PyObject *LIST_INDEX2(PyThreadState *tstate, PyObject *list, PyObject *item);
extern PyObject *LIST_INDEX3(PyThreadState *tstate, PyObject *list, PyObject *item, PyObject *start);
extern PyObject *LIST_INDEX4(PyThreadState *tstate, PyObject *list, PyObject *item, PyObject *start, PyObject *stop);

// Like list.index
extern bool LIST_INSERT(PyThreadState *tstate, PyObject *list, PyObject *index, PyObject *item);
// Like PyList_Insert
extern void LIST_INSERT_CONST(PyObject *list, Py_ssize_t index, PyObject *item);

extern PyObject *MAKE_LIST(PyThreadState *tstate, PyObject *iterable);

extern bool LIST_EXTEND_FROM_LIST(PyObject *list, PyObject *other);

DEVILPY_MAY_BE_UNUSED static PyObject *MAKE_LIST_REPEATED(PyThreadState *tstate, Py_ssize_t size, PyObject *element) {
    PyObject *result = MAKE_LIST_EMPTY(tstate, size);

    if (unlikely(result == NULL)) {
        return NULL;
    }

    for (Py_ssize_t i = 0; i < size; i++) {
        Py_INCREF(element);
        PyList_SET_ITEM(result, i, element);
    }

    return result;
}

#include "lists_generated.h"

#endif


#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Import cache.

This is not about caching the search of modules in the file system, but about
maintaining a cache of module trees built.

It can happen that modules become unused, and then dropped from active modules,
and then later active again, via another import, and in this case, we should
not start anew, but reuse what we already found out about it.
"""

import os

from qutayba.plugins.Plugins import Plugins
from qutayba.utils.Importing import hasPackageDirFilename

imported_modules = {}
imported_by_name = {}


def addImportedModule(imported_module):
    module_filename = os.path.abspath(imported_module.getFilename())

    if hasPackageDirFilename(module_filename):
        module_filename = os.path.dirname(module_filename)

    key = (module_filename, imported_module.getFullName())

    if key in imported_modules:
        assert imported_module is imported_modules[key], key
    else:
        Plugins.onModuleDiscovered(imported_module)

    imported_modules[key] = imported_module
    imported_by_name[imported_module.getFullName()] = imported_module

    # We don't expect that to happen.
    assert not imported_module.isMainModule()


def isImportedModuleByName(full_name):
    return full_name in imported_by_name


def getImportedModuleByName(full_name):
    return imported_by_name[full_name]


def getImportedModuleByNameAndPath(full_name, module_filename):
    if module_filename is None:
        # pyi deps only
        return getImportedModuleByName(full_name)

    # For caching we use absolute paths only.
    module_filename = os.path.abspath(module_filename)

    if hasPackageDirFilename(module_filename):
        module_filename = os.path.dirname(module_filename)

    # KeyError is valid result.
    return imported_modules[module_filename, full_name]


def replaceImportedModule(old, new):
    for key, value in imported_by_name.items():
        if value == old:
            imported_by_name[key] = new
            break
    else:
        assert False, (old, new)

    for key, value in imported_modules.items():
        if value == old:
            imported_modules[key] = new
            break
    else:
        assert False, (old, new)




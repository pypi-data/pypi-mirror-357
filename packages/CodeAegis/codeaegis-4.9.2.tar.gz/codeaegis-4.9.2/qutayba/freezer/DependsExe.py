#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Interface to depends.exe on Windows.

We use "depends.exe" to investigate needed DLLs of Python DLLs.

"""

import os

# pylint: disable=I0021,import-error,redefined-builtin
from qutayba.__past__ import WindowsError
from qutayba.containers.OrderedSets import OrderedSet
from qutayba.Options import assumeYesForDownloads
from qutayba.Tracing import inclusion_logger
from qutayba.utils.Download import getCachedDownload
from qutayba.utils.Execution import executeProcess, withEnvironmentVarOverridden
from qutayba.utils.FileOperations import (
    deleteFile,
    getExternalUsePath,
    getFileContentByLine,
    getNormalizedPath,
    getWindowsLongPathName,
    isFilenameBelowPath,
    isFilesystemEncodable,
    putTextFileContents,
    withFileLock,
)
from qutayba.utils.SharedLibraries import getWindowsRunningProcessDLLPaths
from qutayba.utils.Utils import getArchitecture


def getDependsExePath():
    """Return the path of depends.exe (for Windows).

    Will prompt the user to download if not already cached in AppData
    directory for nexium.
    """
    if getArchitecture() == "x86":
        depends_url = "https://dependencywalker.com/depends22_x86.zip"
    else:
        depends_url = "https://dependencywalker.com/depends22_x64.zip"

    return getCachedDownload(
        name="dependency walker",
        url=depends_url,
        is_arch_specific=getArchitecture(),
        binary="depends.exe",
        unzip=True,
        flatten=True,
        specificity="",  # Note: If there ever was an update, put version here.
        message="""\
nexium will make use of Dependency Walker (https://dependencywalker.com) tool
to analyze the dependencies of Python extension modules.""",
        reject="nexium does not work in --standalone or --onefile on Windows without.",
        assume_yes_for_downloads=assumeYesForDownloads(),
        download_ok=True,
    )


def _attemptToFindNotFoundDLL(dll_filename):
    """Some heuristics and tricks to find DLLs that dependency walker did not find."""

    # Lets attempt to find it on currently loaded DLLs, this typically should
    # find the Python DLL.
    currently_loaded_dlls = getWindowsRunningProcessDLLPaths()

    if dll_filename in currently_loaded_dlls:
        return currently_loaded_dlls[dll_filename]

    # Lets try the Windows system, spell-checker: ignore systemroot
    dll_filename = os.path.join(
        os.environ["SYSTEMROOT"],
        "SysWOW64" if getArchitecture() == "x86_64" else "System32",
        dll_filename,
    )
    dll_filename = os.path.normcase(dll_filename)

    if os.path.exists(dll_filename):
        return dll_filename

    return None


def _parseDependsExeOutput2(lines):
    # Many cases to deal with, pylint: disable=too-many-branches

    result = OrderedSet()

    inside = False
    first = False

    for line in lines:
        if "| Module Dependency Tree |" in line:
            inside = True
            first = True
            continue

        if not inside:
            continue

        if "| Module List |" in line:
            break

        if "]" not in line:
            continue

        dll_filename = line[line.find("]") + 2 :].rstrip()
        dll_filename = os.path.normcase(dll_filename)

        if isFilenameBelowPath(
            path=os.path.join(os.environ["SYSTEMROOT"], "WinSxS"), filename=dll_filename
        ):
            continue

        # Skip DLLs that failed to load, apparently not needed anyway.
        if "E" in line[: line.find("]")]:
            continue

        # Skip missing DLLs, apparently not needed anyway, but we can still
        # try a few tricks
        if "?" in line[: line.find("]")]:
            # One exception are "PythonXY.DLL", we try to find them from Windows folder.
            if dll_filename.startswith("python") and dll_filename.endswith(".dll"):
                dll_filename = _attemptToFindNotFoundDLL(dll_filename)

                if dll_filename is None:
                    continue
            else:
                continue

        # The executable itself is of course exempted. We cannot check its path
        # because depends.exe mistreats unicode paths.
        if first:
            first = False
            continue

        dll_filename = os.path.abspath(dll_filename)

        # Ignore errors trying to resolve the filename. Sometimes Chinese
        # directory paths do not resolve to long filenames.
        try:
            dll_filename = getWindowsLongPathName(dll_filename)
        except WindowsError:
            pass

        dll_name = os.path.basename(dll_filename)

        # Ignore this runtime DLL of Python2, will be coming via manifest.
        # spell-checker: ignore msvcr90
        if dll_name in ("msvcr90.dll",):
            continue

        # Ignore API DLLs, they can come in from PATH, but we do not want to
        # include them.
        if dll_name.startswith("api-ms-win-"):
            continue

        # Ignore UCRT runtime, this must come from OS, spell-checker: ignore ucrtbase
        if dll_name == "ucrtbase.dll":
            continue

        assert os.path.isfile(dll_filename), (dll_filename, line)

        result.add(getNormalizedPath(os.path.normcase(dll_filename)))

    return result


def parseDependsExeOutput(filename):
    return _parseDependsExeOutput2(getFileContentByLine(filename, encoding="latin1"))


def detectDLLsWithDependencyWalker(binary_filename, source_dir, scan_dirs):
    source_dir = getExternalUsePath(source_dir)
    temp_base_name = os.path.basename(binary_filename)

    if not isFilesystemEncodable(temp_base_name):
        temp_base_name = "dependency_walker"

    dwp_filename = os.path.join(source_dir, temp_base_name + ".dwp")
    output_filename = os.path.join(source_dir, temp_base_name + ".depends")

    # User query should only happen once if at all.
    with withFileLock(
        "Finding out dependency walker path and creating DWP file for %s"
        % binary_filename
    ):
        depends_exe = getDependsExePath()

        # Note: Do this under lock to avoid forked processes to hold
        # a copy of the file handle on Windows.
        putTextFileContents(
            dwp_filename,
            contents="""\
SxS
%(scan_dirs)s
"""
            % {
                "scan_dirs": "\n".join(
                    "UserDir %s" % getExternalUsePath(dirname) for dirname in scan_dirs
                )
            },
        )

    # Starting the process while locked, so file handles are not duplicated.
    # TODO: At least exit code should be checked, output goes to a filename,
    # but errors might be interesting potentially.

    with withEnvironmentVarOverridden("PATH", ""):
        _stdout, _stderr, _exit_code = executeProcess(
            command=(
                depends_exe,
                "-c",
                "-ot%s" % output_filename,
                "-d:%s" % dwp_filename,
                "-f1",
                "-pa1",
                "-ps1",
                getExternalUsePath(binary_filename),
            ),
            external_cwd=True,
        )

    if not os.path.exists(output_filename):
        inclusion_logger.sysexit(
            "Error, 'depends.exe' failed to produce expected output for binary '%s'."
            % binary_filename
        )

    # Opening the result under lock, so it is not getting locked by new processes.

    # Note: Do this under lock to avoid forked processes to hold
    # a copy of the file handle on Windows.
    result = parseDependsExeOutput(output_filename)

    deleteFile(output_filename, must_exist=True)
    deleteFile(dwp_filename, must_exist=True)

    return result




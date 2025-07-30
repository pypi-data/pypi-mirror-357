#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - Utility functions for tests."""
# =============================================================================
__author__     = "Daniel Krajzewicz"
__copyright__  = "Copyright 2025, Daniel Krajzewicz"
__credits__    = ["Daniel Krajzewicz"]
__license__    = "GPL"
__version__    = "0.2.0"
__maintainer__ = "Daniel Krajzewicz"
__email__      = "daniel@krajzewicz.de"
__status__     = "Development"
# ===========================================================================
# - https://github.com/dkrajzew/gresiblos
# - http://www.krajzewicz.de
# ===========================================================================


# --- imports ---------------------------------------------------------------
import os
import shutil
import re
import json
import zipfile
from zipfile import ZipFile
TEST_PATH = os.path.split(__file__)[0]
import errno
from pathlib import Path



# --- imports ---------------------------------------------------------------
def pname(string, path="<DIR>"):
    string = string.replace(str(path), "<DIR>").replace("\\", "/")
    return string.replace("__main__.py", "grebakker").replace("pytest", "grebakker").replace("optional arguments", "options")


def tread(filepath):
    return filepath.read_text()

def bread(filepath):
    return filepath.read_bytes()

def pdirtime(string, tmp_path):
    regex = r'([0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?'
    string = string.replace(str(tmp_path), "<DIR>").replace("\\", "/")
    return re.sub(regex, "<DUR>", string)
    
def check_def(tmp_path, content):
    assert tread(tmp_path / "backup" / "d" / "grebakker.json") == content

def prepare(definition, testdata_folder, tmp_path, skipped=[], add_defs={}):
    try:
        shutil.copytree(os.path.join(TEST_PATH, testdata_folder), os.path.join(str(tmp_path), testdata_folder))
    except: pass
    actions = []
    d = json.loads(definition)
    src = Path(tmp_path) / testdata_folder
    dst = Path(tmp_path) / "backup" / d["destination"]
    #os.makedirs(dst)
    for c in [] if "copy" not in d else d["copy"]:
        path = c if type(c)==str else c["name"]
        actions.append(["copy", src / path, dst / path, "skipped" if path in skipped else "<DUR>"])
    for c in [] if "compress" not in d else d["compress"]:
        path = c if type(c)==str else c["name"]
        dur = "skipped" if path in skipped else "<DUR>"
        actions.append(["compress", src / path, dst / (path + ".zip"), dur, path]) # !!!
    for c in [] if "subfolders" not in d else d["subfolders"]:
        path = c if type(c)==str else c["name"]
        actions.append(["sub", src / c, dst / path, "skipped" if path in skipped else "<DUR>"])
        #print(actions[-1])
        #print(tmp_path)
        #print(testdata_folder)
        nactions, _1, _2 = prepare(add_defs[c], os.path.join(testdata_folder, c), tmp_path, skipped=skipped)
        actions.extend(nactions)
    #print ((Path(tmp_path) / testdata_folder / "grebakker.json"))
    (Path(tmp_path) / testdata_folder / "grebakker.json").write_text(definition)
    return actions, str(tmp_path / "backup"), dst



# https://stackoverflow.com/questions/66524269/how-to-compare-files-in-two-zip-file-are-totally-same-or-not
def are_equivalent(filename1, filename2):
    """Compare two ZipFiles to see if they would expand into the same directory structure
    without actually extracting the files.
    """
    
    with ZipFile(filename1, 'r') as zip1, ZipFile(filename2, 'r') as zip2:
        
        # Index items in the ZipFiles by filename. For duplicate filenames, a later
        # item in the ZipFile will overwrite an ealier item; just like a later file
        # will overwrite an earlier file with the same name when extracting.
        zipinfo1 = {info.filename:info for info in zip1.infolist()}
        zipinfo2 = {info.filename:info for info in zip2.infolist()}
        
        # Do some simple checks first
        # Do the ZipFiles contain the same the files?
        assert zipinfo1.keys() == zipinfo2.keys()
        
        # Do the files in the archives have the same CRCs? (This is a 32-bit CRC of the
        # uncompressed item. Is that good enough to confirm the files are the same?)
        if any(zipinfo1[name].CRC != zipinfo2[name].CRC for name in zipinfo1.keys()):
            return False # pragma: no cover
    return True


def check_generated(tmp_path, actions, logpath, logformat, log_head="", testfiles={}):
    # check files
    for action in actions:
        if action[0]=="copy":
            if os.path.isdir(action[1]):
                pass # !!!
            else:
                assert bread(action[1]) == bread(action[2])
        elif action[0]=="compress":
            #c = bread(action[2])
            #with open(f"D:/{os.path.basename(action[2])}", "wb") as fd:
            #    fd.write(c)
            testfile = (action[4] + ".zip") if action[4] not in testfiles else testfiles[action[4]]
            """
            os.makedirs(os.path.join(tmp_path, "tmp_zip"), exist_ok=True)
            with zipfile.ZipFile(Path(TEST_PATH) / testfile, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(tmp_path, "tmp_zip"))
            zipf = zipfile.ZipFile(os.path.join(tmp_path, "tmp.zip"), "w", zipfile.ZIP_DEFLATED, compresslevel=9)
            for root, dirs, files in os.walk(os.path.join(tmp_path, "tmp_zip")):
                for file in files:
                    srcf = os.path.join(root, file)
                    dstf = os.path.relpath(os.path.join(root, file), os.path.join(tmp_path, "tmp_zip"))
                    zipf.write(srcf, dstf)
            zipf.close()
            c = bread(Path(os.path.join(tmp_path, "tmp.zip")))
            with open(f"D:/tmp.zip", "wb") as fd:
                fd.write(c)
            """
            assert are_equivalent(os.path.join(TEST_PATH, testfile), str(action[2]))
            #assert bread(Path(os.path.join(tmp_path, "tmp.zip"))) == bread(action[2])
            #assert bread(Path(TEST_PATH) / testfile) == bread(action[2])
        elif action[0]=="sub":
            continue
        else:
            raise ValueError(f"unknown action '{action[0]}'") # pragma: no cover
    # check log
    log = None
    if logformat=="csv":
        log = [f'"{action[0]}";"{action[1]}";"{action[2]}";"{action[3]}"' for action in actions]
        log = log_head + "\n".join(log) + "\n"
    elif logformat=="json":
        log = ['    {"action": "' + action[0] + '", "src": "' + str(action[1]) + '", "dst": "' + str(action[2]) + '", "duration": "' + str(action[3]) + '"}' for action in actions]
        log = log_head + "[\n" + ",\n".join(log) + "\n]\n"
    elif logformat=="off":
        pass
    else:
        raise ValueError(f"unknown log format '{logformat}'") # pragma: no cover
    if log is not None:
        is_log = pdirtime(tread(logpath / "grebakker_log.csv"), tmp_path)
        shall_log = pdirtime(log, tmp_path)
        #(Path("d:\\is_log.txt")).write_text(is_log)
        #(Path("d:\\shall_log.txt")).write_text(shall_log)
        #print (is_log)
        #print ("---------------------------")
        #print (shall_log)
        assert is_log == shall_log
    else:
        assert not os.path.exists(logpath / "grebakker_log.csv")
    #assert tread(tmp_path / "dest" / "d" / "grebakker.json") == content


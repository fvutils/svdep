import json
import os
import pathlib
import pytest
import pytest_fv as pfv
from pytest_fv.fixtures import *
import shutil
from svdep import TaskBuildFileCollection, TaskCheckUpToDate
import time

def test_smoke(dirconfig : pfv.DirConfig):

    data_dir = os.path.join(dirconfig.test_srcdir(), "data/test_smoke")

    largest_timestamp = 0
    for file in ["smoke1.sv", "smoke2.sv", "foo.svh"]:
        ts = os.path.getmtime(os.path.join(data_dir, file))
        if ts > largest_timestamp:
            largest_timestamp = ts

    info = TaskBuildFileCollection([
        os.path.join(data_dir, "smoke1.sv"),
        os.path.join(data_dir, "smoke2.sv")]).build()

    ret = TaskCheckUpToDate([
        os.path.join(data_dir, "smoke1.sv"),
        os.path.join(data_dir, "smoke2.sv")]).check(info, largest_timestamp)
    assert ret == True

def test_smoke_drop_file(dirconfig : pfv.DirConfig):

    data_dir = os.path.join(dirconfig.test_srcdir(), "data/test_smoke")

    largest_timestamp = 0
    for file in ["smoke1.sv", "smoke2.sv"]:
        ts = os.path.getmtime(os.path.join(data_dir, file))
        if ts > largest_timestamp:
            largest_timestamp = ts

    info = TaskBuildFileCollection([
        os.path.join(data_dir, "smoke1.sv"),
        os.path.join(data_dir, "smoke2.sv")]).build()

    # New compilation list has fewer files. Expect up-to-date to fail
    ret = TaskCheckUpToDate([os.path.join(data_dir, "smoke2.sv")]).check(info, largest_timestamp)
    assert ret == False

def test_smoke_add_file(dirconfig : pfv.DirConfig):

    data_dir = os.path.join(dirconfig.test_srcdir(), "data/test_smoke")

    largest_timestamp = 0
    for file in ["smoke1.sv", "smoke2.sv"]:
        ts = os.path.getmtime(os.path.join(data_dir, file))
        if ts > largest_timestamp:
            largest_timestamp = ts

    info = TaskBuildFileCollection([
        os.path.join(data_dir, "smoke1.sv"),
        os.path.join(data_dir, "smoke2.sv")]).build()

    # New compilation list has fewer files. Expect up-to-date to fail
    ret = TaskCheckUpToDate([
        os.path.join(data_dir, "smoke1.sv"),
        os.path.join(data_dir, "smoke2.sv"),
        os.path.join(data_dir, "smoke3.sv")
        ]).check(info, largest_timestamp)
    assert ret == False

def test_smoke_mod_file(dirconfig : pfv.DirConfig):

    data_dir = os.path.join(dirconfig.test_srcdir(), "data/test_smoke")

    shutil.copytree(
        data_dir,
        dirconfig.rundir(),
        dirs_exist_ok=True)

    largest_timestamp = 0
    for file in ["smoke1.sv", "smoke2.sv", "smoke3.sv", "foo.svh"]:
        ts = os.path.getmtime(os.path.join(dirconfig.rundir(), file))
        if ts > largest_timestamp:
            largest_timestamp = ts

    info = TaskBuildFileCollection([
        os.path.join(dirconfig.rundir(), "smoke1.sv"),
        os.path.join(dirconfig.rundir(), "smoke2.sv"),
        os.path.join(dirconfig.rundir(), "smoke3.sv")]).build()

    time.sleep(50/1000)

    pathlib.Path(os.path.join(dirconfig.rundir(), "smoke2.sv")).touch()

    # smoke2.sv has changed. See if it is detected
    ret = TaskCheckUpToDate([
        os.path.join(data_dir, "smoke1.sv"),
        os.path.join(data_dir, "smoke2.sv"),
        os.path.join(data_dir, "smoke3.sv")
        ]).check(info, largest_timestamp)
    assert ret == False

def test_uvm(dirconfig : pfv.DirConfig):
    uvm_dir = os.path.abspath(os.path.join(
        dirconfig.test_srcdir(), "../packages/uvm"))

    info = TaskBuildFileCollection([
        os.path.join(uvm_dir, "src/uvm_pkg.sv")],
        incdirs=[
            os.path.join(uvm_dir, "src")]).build()
#    print("files: %s ; info: %s" % (
#        str(info.root_files),
#        str(info.file_info)))
    print("info: %s" % str(json.dumps(info.to_dict())))



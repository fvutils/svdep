import json
import os
import pytest
import pytest_fv as pfv
from pytest_fv.fixtures import *
from svdep import TaskBuildFileCollection, TaskCheckUpToDate

def test_smoke(dirconfig : pfv.DirConfig):

    data_dir = os.path.join(dirconfig.test_srcdir(), "data/test_smoke")

    largest_timestamp = 0
    for file in ["smoke1.sv", "smoke2.sv"]:
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

    ret = TaskCheckUpToDate([os.path.join(data_dir, "smoke2.sv")]).check(info, largest_timestamp)
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



import json
import os
import pathlib
import pytest
import shutil
from svdep import TaskBuildFileCollection, TaskCheckUpToDate
import time

@pytest.fixture
def test_srcdir():
    """Return the directory containing test files."""
    return os.path.dirname(__file__)

@pytest.fixture
def rundir(tmp_path):
    """Return a temporary run directory for the test."""
    return tmp_path

def test_smoke(test_srcdir):

    data_dir = os.path.join(test_srcdir, "data/test_smoke")

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

def test_smoke_drop_file(test_srcdir):

    data_dir = os.path.join(test_srcdir, "data/test_smoke")

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

def test_smoke_add_file(test_srcdir):

    data_dir = os.path.join(test_srcdir, "data/test_smoke")

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

def test_smoke_mod_file(test_srcdir, rundir):

    data_dir = os.path.join(test_srcdir, "data/test_smoke")

    shutil.copytree(
        data_dir,
        rundir,
        dirs_exist_ok=True)

    largest_timestamp = 0
    for file in ["smoke1.sv", "smoke2.sv", "smoke3.sv", "foo.svh"]:
        ts = os.path.getmtime(os.path.join(rundir, file))
        if ts > largest_timestamp:
            largest_timestamp = ts

    info = TaskBuildFileCollection([
        os.path.join(rundir, "smoke1.sv"),
        os.path.join(rundir, "smoke2.sv"),
        os.path.join(rundir, "smoke3.sv")]).build()

    time.sleep(50/1000)

    pathlib.Path(os.path.join(rundir, "smoke2.sv")).touch()

    # smoke2.sv has changed. See if it is detected
    ret = TaskCheckUpToDate([
        os.path.join(data_dir, "smoke1.sv"),
        os.path.join(data_dir, "smoke2.sv"),
        os.path.join(data_dir, "smoke3.sv")
        ]).check(info, largest_timestamp)
    assert ret == False

def test_uvm(test_srcdir):
    uvm_dir = os.path.abspath(os.path.join(
        test_srcdir, "../packages/uvm"))

    info = TaskBuildFileCollection([
        os.path.join(uvm_dir, "src/uvm_pkg.sv")],
        incdirs=[
            os.path.join(uvm_dir, "src")]).build()
#    print("files: %s ; info: %s" % (
#        str(info.root_files),
#        str(info.file_info)))
    print("info: %s" % str(json.dumps(info.to_dict())))

def test_uvm_dump_load(test_srcdir):
    from io import StringIO
    from svdep import FileCollection
    uvm_dir = os.path.abspath(os.path.join(
        test_srcdir, "../packages/uvm"))

    info = TaskBuildFileCollection([
        os.path.join(uvm_dir, "src/uvm_pkg.sv")],
        incdirs=[
            os.path.join(uvm_dir, "src")]).build()
    
    info_d = info.to_dict()
    out = StringIO()
    json.dump(info_d, out)
    info_load_d = json.loads(out.getvalue())
    info_load = FileCollection.from_dict(info_load_d)
#    print("files: %s ; info: %s" % (
#        str(info.root_files),
#        str(info.file_info)))
    print("info_load: %s" % str(info_load))

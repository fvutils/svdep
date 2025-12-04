"""
test_native_basic.py - Basic tests for the native SVDep library
"""
import json
import os
import pytest

def test_create_destroy(svdep_lib):
    """Test basic context creation and destruction."""
    ctx = svdep_lib.svdep_create()
    assert ctx is not None
    svdep_lib.svdep_destroy(ctx)

def test_add_incdir(svdep_lib, svdep_ctx, test_data_dir):
    """Test adding include directories."""
    result = svdep_lib.svdep_add_incdir(svdep_ctx, str(test_data_dir).encode())
    assert result == 0

def test_add_root_file(svdep_lib, svdep_ctx, test_data_dir):
    """Test adding root files."""
    smoke1 = test_data_dir / "smoke1.sv"
    result = svdep_lib.svdep_add_root_file(svdep_ctx, str(smoke1).encode())
    assert result == 0

def test_build_simple(svdep_lib, svdep_ctx, test_data_dir):
    """Test building a simple file collection."""
    smoke1 = test_data_dir / "smoke1.sv"
    
    svdep_lib.svdep_add_incdir(svdep_ctx, str(test_data_dir).encode())
    svdep_lib.svdep_add_root_file(svdep_ctx, str(smoke1).encode())
    
    result = svdep_lib.svdep_build(svdep_ctx)
    assert result == 0
    
    json_str = svdep_lib.svdep_get_json(svdep_ctx)
    assert json_str is not None
    
    data = json.loads(json_str.decode())
    assert "root_files" in data
    assert "file_info" in data
    assert len(data["root_files"]) == 1
    assert data["root_files"][0]["name"] == str(smoke1)

def test_build_with_includes(svdep_lib, svdep_ctx, test_data_dir):
    """Test building a file collection with includes."""
    smoke1 = test_data_dir / "smoke1.sv"
    foo_svh = test_data_dir / "foo.svh"
    
    svdep_lib.svdep_add_incdir(svdep_ctx, str(test_data_dir).encode())
    svdep_lib.svdep_add_root_file(svdep_ctx, str(smoke1).encode())
    
    result = svdep_lib.svdep_build(svdep_ctx)
    assert result == 0
    
    json_str = svdep_lib.svdep_get_json(svdep_ctx)
    data = json.loads(json_str.decode())
    
    # Check that the include was found
    root_info = data["root_files"][0]
    assert len(root_info["includes"]) == 1
    assert str(foo_svh) in root_info["includes"][0]

def test_build_multiple_files(svdep_lib, svdep_ctx, test_data_dir):
    """Test building with multiple root files."""
    smoke1 = test_data_dir / "smoke1.sv"
    smoke2 = test_data_dir / "smoke2.sv"
    
    svdep_lib.svdep_add_incdir(svdep_ctx, str(test_data_dir).encode())
    svdep_lib.svdep_add_root_file(svdep_ctx, str(smoke1).encode())
    svdep_lib.svdep_add_root_file(svdep_ctx, str(smoke2).encode())
    
    result = svdep_lib.svdep_build(svdep_ctx)
    assert result == 0
    
    json_str = svdep_lib.svdep_get_json(svdep_ctx)
    data = json.loads(json_str.decode())
    
    assert len(data["root_files"]) == 2

def test_json_load(svdep_lib, svdep_ctx, test_data_dir):
    """Test loading from JSON."""
    smoke1 = test_data_dir / "smoke1.sv"
    
    svdep_lib.svdep_add_incdir(svdep_ctx, str(test_data_dir).encode())
    svdep_lib.svdep_add_root_file(svdep_ctx, str(smoke1).encode())
    svdep_lib.svdep_build(svdep_ctx)
    
    json_str = svdep_lib.svdep_get_json(svdep_ctx)
    
    # Create a new context and load the JSON
    ctx2 = svdep_lib.svdep_create()
    result = svdep_lib.svdep_load_json(ctx2, json_str)
    assert result == 0
    
    json_str2 = svdep_lib.svdep_get_json(ctx2)
    svdep_lib.svdep_destroy(ctx2)
    
    # Compare the JSON outputs
    data1 = json.loads(json_str.decode())
    data2 = json.loads(json_str2.decode())
    
    assert len(data1["root_files"]) == len(data2["root_files"])
    assert len(data1["file_info"]) == len(data2["file_info"])

def test_check_up_to_date(svdep_lib, svdep_ctx, test_data_dir):
    """Test checking if files are up to date."""
    smoke1 = test_data_dir / "smoke1.sv"
    
    svdep_lib.svdep_add_incdir(svdep_ctx, str(test_data_dir).encode())
    svdep_lib.svdep_add_root_file(svdep_ctx, str(smoke1).encode())
    svdep_lib.svdep_build(svdep_ctx)
    
    json_str = svdep_lib.svdep_get_json(svdep_ctx)
    
    # Get the largest timestamp
    import time
    largest_timestamp = time.time()
    
    # Create a new context, load JSON, and check
    ctx2 = svdep_lib.svdep_create()
    svdep_lib.svdep_load_json(ctx2, json_str)
    svdep_lib.svdep_add_root_file(ctx2, str(smoke1).encode())
    
    result = svdep_lib.svdep_check_up_to_date(ctx2, largest_timestamp)
    svdep_lib.svdep_destroy(ctx2)
    
    assert result == 1  # Should be up to date

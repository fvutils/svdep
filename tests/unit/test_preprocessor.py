"""
test_preprocessor.py - Tests for the preprocessor functionality
"""
import json
import os
import pytest
import tempfile
import shutil
from pathlib import Path

def test_ifdef_active(svdep_lib, test_data_dir):
    """Test ifdef directive when macro is defined."""
    # Create test file with ifdef
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        test_file.write_text('''
`define MY_MACRO
`ifdef MY_MACRO
`include "foo.svh"
`endif
''')
        # Copy foo.svh to temp directory
        shutil.copy(test_data_dir / "foo.svh", tmpdir)
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # The include should be found since MY_MACRO is defined
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1

def test_ifdef_inactive(svdep_lib, test_data_dir):
    """Test ifdef directive when macro is not defined."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        test_file.write_text('''
`ifdef MY_MACRO
`include "foo.svh"
`endif
''')
        shutil.copy(test_data_dir / "foo.svh", tmpdir)
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # The include should NOT be found since MY_MACRO is not defined
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 0

def test_ifndef(svdep_lib, test_data_dir):
    """Test ifndef directive."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        test_file.write_text('''
`ifndef MY_MACRO
`include "foo.svh"
`endif
''')
        shutil.copy(test_data_dir / "foo.svh", tmpdir)
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # The include SHOULD be found since MY_MACRO is not defined
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1

def test_else_branch(svdep_lib, test_data_dir):
    """Test else branch of ifdef."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        bar_svh = Path(tmpdir) / "bar.svh"
        
        test_file.write_text('''
`ifdef MY_MACRO
`include "bar.svh"
`else
`include "foo.svh"
`endif
''')
        foo_svh.write_text("// foo.svh\n")
        bar_svh.write_text("// bar.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # Should find foo.svh (else branch) not bar.svh
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]

def test_nested_ifdef(svdep_lib, test_data_dir):
    """Test nested ifdef directives."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        
        test_file.write_text('''
`define OUTER
`ifdef OUTER
    `ifdef INNER
    `include "bar.svh"
    `else
    `include "foo.svh"
    `endif
`endif
''')
        foo_svh.write_text("// foo.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # OUTER is defined, INNER is not, so foo.svh should be included
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]

def test_line_comment(svdep_lib, test_data_dir):
    """Test that line comments are handled correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        
        test_file.write_text('''
// This is a comment
// `include "notreal.svh"
`include "foo.svh"  // Include foo
''')
        foo_svh.write_text("// foo.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # Only foo.svh should be included
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]

def test_block_comment(svdep_lib, test_data_dir):
    """Test that block comments are handled correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        
        test_file.write_text('''
/* This is a block comment
   `include "notreal.svh"
   spanning multiple lines */
`include "foo.svh"
''')
        foo_svh.write_text("// foo.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # Only foo.svh should be included
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]


def test_ifdef_protected_missing_include(svdep_lib):
    """Test that missing includes protected by ifdef are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        
        # Include a non-existent file, but protected by ifdef
        test_file.write_text('''
`ifdef NEVER_DEFINED
`include "missing_file.svh"
`endif

module test;
endmodule
''')
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # No includes should be found since ifdef is false
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 0


def test_ifndef_protected_missing_include(svdep_lib):
    """Test that missing includes protected by ifndef (when macro is defined) are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        
        test_file.write_text('''
`define SKIP_MISSING
`ifndef SKIP_MISSING
`include "nonexistent.svh"
`endif

module test;
endmodule
''')
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # No includes - ifndef is false because SKIP_MISSING is defined
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 0


def test_else_branch_protected_missing_include(svdep_lib):
    """Test that missing includes in else branch are skipped when if is true."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        
        test_file.write_text('''
`define USE_FOO
`ifdef USE_FOO
`include "foo.svh"
`else
`include "does_not_exist.svh"
`endif
''')
        foo_svh.write_text("// foo.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # Only foo.svh should be included, not the missing file
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]


def test_nested_ifdef_protected_missing_includes(svdep_lib):
    """Test nested ifdef protecting multiple missing includes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        
        test_file.write_text('''
`define OUTER_DEFINED
`ifdef OUTER_DEFINED
    `ifdef INNER_NOT_DEFINED
    `include "missing1.svh"
    `include "missing2.svh"
    `else
    `include "foo.svh"
    `endif
`else
    `include "missing3.svh"
`endif
''')
        foo_svh.write_text("// foo.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # Only foo.svh should be included
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]


def test_multiple_ifdef_protected_missing_includes(svdep_lib):
    """Test multiple separate ifdef blocks protecting missing includes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        
        test_file.write_text('''
`ifdef FEATURE_A
`include "feature_a.svh"
`endif

`include "foo.svh"

`ifdef FEATURE_B
`include "feature_b.svh"
`endif

`ifdef FEATURE_C
`include "feature_c.svh"
`endif
''')
        foo_svh.write_text("// foo.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # Only foo.svh should be included
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]


def test_elsif_protected_missing_include(svdep_lib):
    """Test elsif branch protecting missing includes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        
        test_file.write_text('''
`define USE_FOO
`ifdef USE_BAR
`include "bar.svh"
`elsif USE_FOO
`include "foo.svh"
`else
`include "default.svh"
`endif
''')
        foo_svh.write_text("// foo.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # Only foo.svh from elsif branch
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]


def test_undef_then_ifdef_protected_missing(svdep_lib):
    """Test that undef properly disables ifdef protection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.sv"
        foo_svh = Path(tmpdir) / "foo.svh"
        
        test_file.write_text('''
`define MY_FEATURE
`undef MY_FEATURE
`ifdef MY_FEATURE
`include "missing.svh"
`else
`include "foo.svh"
`endif
''')
        foo_svh.write_text("// foo.svh\n")
        
        ctx = svdep_lib.svdep_create()
        svdep_lib.svdep_add_incdir(ctx, tmpdir.encode())
        svdep_lib.svdep_add_root_file(ctx, str(test_file).encode())
        
        result = svdep_lib.svdep_build(ctx)
        assert result == 0
        
        json_str = svdep_lib.svdep_get_json(ctx)
        data = json.loads(json_str.decode())
        svdep_lib.svdep_destroy(ctx)
        
        # foo.svh from else branch (MY_FEATURE was undefined)
        root_info = data["root_files"][0]
        assert len(root_info["includes"]) == 1
        assert "foo.svh" in root_info["includes"][0]

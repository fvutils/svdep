"""
test_performance.py - Performance comparison tests between Python and native implementations

These tests compare the performance of the pure Python implementation versus
the native C++ implementation using the UVM library as a realistic workload.
"""
import json
import os
import time
import ctypes
import pytest
from pathlib import Path


def get_uvm_dir():
    """Get the path to the UVM source directory."""
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent
    uvm_dir = project_root / "packages" / "uvm"
    if not uvm_dir.exists():
        pytest.skip("UVM package not found")
    return uvm_dir


def find_library():
    """Find the svdep shared library."""
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent
    
    possible_paths = [
        project_root / "cpp" / "build" / "libsvdep.so",
        project_root / "cpp" / "build" / "libsvdep.dylib",
        project_root / "cpp" / "build" / "Debug" / "svdep.dll",
        project_root / "cpp" / "build" / "Release" / "svdep.dll",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    return None


@pytest.fixture(scope="module")
def uvm_dir():
    """Fixture for UVM directory."""
    return get_uvm_dir()


@pytest.fixture(scope="module")
def native_lib():
    """Load the native library."""
    lib_path = find_library()
    if lib_path is None:
        pytest.skip("Native library not found")
    
    lib = ctypes.CDLL(lib_path)
    
    lib.svdep_create.restype = ctypes.c_void_p
    lib.svdep_create.argtypes = []
    lib.svdep_destroy.restype = None
    lib.svdep_destroy.argtypes = [ctypes.c_void_p]
    lib.svdep_add_incdir.restype = ctypes.c_int
    lib.svdep_add_incdir.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.svdep_add_root_file.restype = ctypes.c_int
    lib.svdep_add_root_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.svdep_build.restype = ctypes.c_int
    lib.svdep_build.argtypes = [ctypes.c_void_p]
    lib.svdep_get_json.restype = ctypes.c_char_p
    lib.svdep_get_json.argtypes = [ctypes.c_void_p]
    lib.svdep_load_json.restype = ctypes.c_int
    lib.svdep_load_json.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.svdep_check_up_to_date.restype = ctypes.c_int
    lib.svdep_check_up_to_date.argtypes = [ctypes.c_void_p, ctypes.c_double]
    
    return lib


def run_python_impl(uvm_dir, iterations=1):
    """Run the Python implementation and return timing info."""
    import sys
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent
    sys.path.insert(0, str(project_root / "src"))
    
    from svdep import TaskBuildFileCollection
    
    uvm_pkg = uvm_dir / "src" / "uvm_pkg.sv"
    uvm_src = uvm_dir / "src"
    
    times = []
    result_data = None
    
    for _ in range(iterations):
        start = time.perf_counter()
        info = TaskBuildFileCollection(
            [str(uvm_pkg)],
            incdirs=[str(uvm_src)]
        ).build()
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        result_data = info.to_dict()
    
    return {
        "times": times,
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "num_files": len(result_data["file_info"]),
        "num_root_files": len(result_data["root_files"]),
    }


def run_native_impl(native_lib, uvm_dir, iterations=1):
    """Run the native implementation and return timing info."""
    uvm_pkg = uvm_dir / "src" / "uvm_pkg.sv"
    uvm_src = uvm_dir / "src"
    
    times = []
    result_data = None
    
    for _ in range(iterations):
        ctx = native_lib.svdep_create()
        
        start = time.perf_counter()
        native_lib.svdep_add_incdir(ctx, str(uvm_src).encode())
        native_lib.svdep_add_root_file(ctx, str(uvm_pkg).encode())
        native_lib.svdep_build(ctx)
        elapsed = time.perf_counter() - start
        
        json_str = native_lib.svdep_get_json(ctx)
        result_data = json.loads(json_str.decode())
        
        native_lib.svdep_destroy(ctx)
        times.append(elapsed)
    
    return {
        "times": times,
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "num_files": len(result_data["file_info"]),
        "num_root_files": len(result_data["root_files"]),
    }


class TestPerformanceComparison:
    """Performance comparison tests."""
    
    def test_uvm_single_run_comparison(self, native_lib, uvm_dir):
        """Compare single run performance on UVM."""
        # Run Python implementation
        python_result = run_python_impl(uvm_dir, iterations=1)
        
        # Run native implementation
        native_result = run_native_impl(native_lib, uvm_dir, iterations=1)
        
        # Note: Python implementation ignores ifdef/ifndef and collects ALL includes,
        # while native implementation respects conditional compilation.
        # Native may find slightly fewer files (more accurate behavior).
        # Allow up to 5% difference in file count.
        file_diff = abs(python_result["num_files"] - native_result["num_files"])
        max_diff = max(python_result["num_files"], native_result["num_files"]) * 0.05
        assert file_diff <= max_diff, \
            f"File count difference too large: Python={python_result['num_files']}, Native={native_result['num_files']}"
        
        speedup = python_result["avg_time"] / native_result["avg_time"]
        
        print(f"\n{'='*60}")
        print(f"UVM Single Run Performance Comparison")
        print(f"{'='*60}")
        print(f"Python files:    {python_result['num_files']}")
        print(f"Native files:    {native_result['num_files']}")
        print(f"  (Native respects ifdef/ifndef, Python ignores them)")
        print(f"Python time:     {python_result['avg_time']*1000:.2f} ms")
        print(f"Native time:     {native_result['avg_time']*1000:.2f} ms")
        print(f"Speedup:         {speedup:.2f}x")
        print(f"{'='*60}")
    
    def test_uvm_multiple_runs_comparison(self, native_lib, uvm_dir):
        """Compare multiple run performance on UVM to get stable averages."""
        iterations = 5
        
        # Run Python implementation
        python_result = run_python_impl(uvm_dir, iterations=iterations)
        
        # Run native implementation
        native_result = run_native_impl(native_lib, uvm_dir, iterations=iterations)
        
        speedup = python_result["avg_time"] / native_result["avg_time"]
        
        print(f"\n{'='*60}")
        print(f"UVM Performance Comparison ({iterations} iterations)")
        print(f"{'='*60}")
        print(f"Files processed: {native_result['num_files']}")
        print(f"")
        print(f"Python implementation:")
        print(f"  Average: {python_result['avg_time']*1000:.2f} ms")
        print(f"  Min:     {python_result['min_time']*1000:.2f} ms")
        print(f"  Max:     {python_result['max_time']*1000:.2f} ms")
        print(f"")
        print(f"Native implementation:")
        print(f"  Average: {native_result['avg_time']*1000:.2f} ms")
        print(f"  Min:     {native_result['min_time']*1000:.2f} ms")
        print(f"  Max:     {native_result['max_time']*1000:.2f} ms")
        print(f"")
        print(f"Speedup: {speedup:.2f}x faster")
        print(f"{'='*60}")
    
    def test_json_serialization_comparison(self, native_lib, uvm_dir):
        """Compare JSON serialization performance."""
        # First build with both implementations
        python_result = run_python_impl(uvm_dir, iterations=1)
        
        # For native, we need to time JSON generation separately
        uvm_pkg = uvm_dir / "src" / "uvm_pkg.sv"
        uvm_src = uvm_dir / "src"
        
        ctx = native_lib.svdep_create()
        native_lib.svdep_add_incdir(ctx, str(uvm_src).encode())
        native_lib.svdep_add_root_file(ctx, str(uvm_pkg).encode())
        native_lib.svdep_build(ctx)
        
        # Time JSON generation
        iterations = 10
        native_json_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            json_str = native_lib.svdep_get_json(ctx)
            elapsed = time.perf_counter() - start
            native_json_times.append(elapsed)
        
        native_lib.svdep_destroy(ctx)
        
        # Time Python JSON generation
        import sys
        test_dir = Path(__file__).parent
        project_root = test_dir.parent.parent
        sys.path.insert(0, str(project_root / "src"))
        from svdep import TaskBuildFileCollection
        
        info = TaskBuildFileCollection(
            [str(uvm_pkg)],
            incdirs=[str(uvm_src)]
        ).build()
        
        python_json_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            _ = json.dumps(info.to_dict())
            elapsed = time.perf_counter() - start
            python_json_times.append(elapsed)
        
        native_avg = sum(native_json_times) / len(native_json_times)
        python_avg = sum(python_json_times) / len(python_json_times)
        speedup = python_avg / native_avg if native_avg > 0 else float('inf')
        
        print(f"\n{'='*60}")
        print(f"JSON Serialization Performance ({iterations} iterations)")
        print(f"{'='*60}")
        print(f"Python average: {python_avg*1000:.4f} ms")
        print(f"Native average: {native_avg*1000:.4f} ms")
        print(f"Speedup:        {speedup:.2f}x")
        print(f"{'='*60}")


class TestPerformanceRegression:
    """Performance regression tests with thresholds."""
    
    def test_native_uvm_under_threshold(self, native_lib, uvm_dir):
        """Ensure native implementation processes UVM under a reasonable threshold."""
        # Run native implementation
        result = run_native_impl(native_lib, uvm_dir, iterations=3)
        
        # Native should process UVM in under 100ms on modern hardware
        threshold_ms = 100
        assert result["avg_time"] * 1000 < threshold_ms, \
            f"Native implementation too slow: {result['avg_time']*1000:.2f}ms > {threshold_ms}ms"
        
        print(f"\nNative UVM processing: {result['avg_time']*1000:.2f}ms (threshold: {threshold_ms}ms)")
    
    def test_native_faster_than_python(self, native_lib, uvm_dir):
        """Ensure native implementation is faster than Python."""
        python_result = run_python_impl(uvm_dir, iterations=3)
        native_result = run_native_impl(native_lib, uvm_dir, iterations=3)
        
        speedup = python_result["avg_time"] / native_result["avg_time"]
        
        # Native should be at least 2x faster
        min_speedup = 2.0
        assert speedup >= min_speedup, \
            f"Native implementation not fast enough: {speedup:.2f}x < {min_speedup}x"
        
        print(f"\nNative speedup: {speedup:.2f}x (minimum required: {min_speedup}x)")


class TestOutputEquivalence:
    """Tests to ensure Python and native implementations produce equivalent output."""
    
    def test_uvm_output_equivalence(self, native_lib, uvm_dir):
        """Ensure both implementations produce similar results for UVM.
        
        Note: The Python implementation ignores ifdef/ifndef directives and collects
        ALL includes unconditionally. The native implementation respects conditional
        compilation and only collects includes from active code paths.
        
        This means native may find slightly fewer files (more accurate behavior).
        We verify that all files found by native are also found by Python.
        """
        # Run Python implementation
        import sys
        test_dir = Path(__file__).parent
        project_root = test_dir.parent.parent
        sys.path.insert(0, str(project_root / "src"))
        from svdep import TaskBuildFileCollection
        
        uvm_pkg = uvm_dir / "src" / "uvm_pkg.sv"
        uvm_src = uvm_dir / "src"
        
        python_info = TaskBuildFileCollection(
            [str(uvm_pkg)],
            incdirs=[str(uvm_src)]
        ).build()
        python_data = python_info.to_dict()
        
        # Run native implementation
        ctx = native_lib.svdep_create()
        native_lib.svdep_add_incdir(ctx, str(uvm_src).encode())
        native_lib.svdep_add_root_file(ctx, str(uvm_pkg).encode())
        native_lib.svdep_build(ctx)
        native_json = native_lib.svdep_get_json(ctx)
        native_data = json.loads(native_json.decode())
        native_lib.svdep_destroy(ctx)
        
        python_files = set(python_data["file_info"].keys())
        native_files = set(native_data["file_info"].keys())
        
        # All native files should be in Python (Python over-collects)
        missing_in_python = native_files - python_files
        assert not missing_in_python, f"Files in Native but not Python: {missing_in_python}"
        
        # Extra files in Python are due to ignoring ifdef/ifndef (expected)
        extra_in_python = python_files - native_files
        
        print(f"\n{'='*60}")
        print(f"Output Equivalence Check")
        print(f"{'='*60}")
        print(f"Python files: {len(python_files)}")
        print(f"Native files: {len(native_files)}")
        if extra_in_python:
            print(f"Extra in Python (due to ignoring ifdef): {len(extra_in_python)}")
            for f in sorted(extra_in_python):
                print(f"  - {Path(f).name}")
        print(f"{'='*60}")
        
        # For files found by both, compare includes
        common_files = python_files & native_files
        include_mismatches = []
        
        for path in common_files:
            python_includes = set(python_data["file_info"][path]["includes"])
            native_includes = set(native_data["file_info"][path]["includes"])
            
            # Native includes should be subset of Python includes
            extra_native = native_includes - python_includes
            if extra_native:
                include_mismatches.append((path, extra_native))
        
        assert not include_mismatches, \
            f"Include mismatches found: {include_mismatches}"
        
        print(f"Common files verified: {len(common_files)}")

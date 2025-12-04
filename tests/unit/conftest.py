"""
conftest.py - Pytest configuration for unit tests
"""
import os
import pytest
import ctypes
from pathlib import Path

def find_library():
    """Find the svdep shared library."""
    # Get the project root
    test_dir = Path(__file__).parent
    project_root = test_dir.parent.parent
    
    # Look for the library in common build locations
    possible_paths = [
        project_root / "cpp" / "build" / "libsvdep.so",
        project_root / "cpp" / "build" / "libsvdep.dylib",
        project_root / "cpp" / "build" / "Debug" / "svdep.dll",
        project_root / "cpp" / "build" / "Release" / "svdep.dll",
        project_root / "cpp" / "build" / "Release" / "libsvdep.so",
        project_root / "cpp" / "build" / "Release" / "libsvdep.dylib",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # Also check if it's installed in system paths
    import platform
    if platform.system() == "Linux":
        system_paths = ["/usr/local/lib/libsvdep.so", "/usr/lib/libsvdep.so"]
    elif platform.system() == "Darwin":
        system_paths = ["/usr/local/lib/libsvdep.dylib"]
    else:
        system_paths = []
    
    for path in system_paths:
        if os.path.exists(path):
            return path
    
    return None

@pytest.fixture(scope="session")
def svdep_lib():
    """Load the svdep shared library."""
    lib_path = find_library()
    if lib_path is None:
        pytest.skip("svdep library not found. Build it first with: cd cpp && mkdir build && cd build && cmake .. && make")
    
    lib = ctypes.CDLL(lib_path)
    
    # Set up function signatures
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
    
    lib.svdep_get_error.restype = ctypes.c_char_p
    lib.svdep_get_error.argtypes = [ctypes.c_void_p]
    
    return lib

@pytest.fixture
def svdep_ctx(svdep_lib):
    """Create and return an SVDep context, automatically cleaned up."""
    ctx = svdep_lib.svdep_create()
    yield ctx
    svdep_lib.svdep_destroy(ctx)

@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent.parent / "data" / "test_smoke"

Overview
========

Purpose
-------

**svdep** is a SystemVerilog dependency-management tool designed to determine whether 
a set of SystemVerilog files has been modified and needs recompilation. It parses 
SystemVerilog files to identify ``\`include`` directives and builds a dependency tree 
of all included files along with their timestamps.

The tool operates in two modes:

- **Clean mode**: No existing dependency information exists. svdep scans all root files 
  and their includes, producing a JSON file that captures the include tree and timestamps.

- **Check mode**: Dependency information exists from a previous run. svdep checks whether 
  any files in the dependency tree have been modified since the last build.

Features
--------

- Parses SystemVerilog ``\`include`` directives to build a complete dependency tree
- Tracks file modification timestamps
- Supports both pure-Python and native C++ implementations
- Automatically uses the native implementation when available for improved performance
- Produces JSON output for caching and incremental builds

Installation
------------

Install svdep using pip:

.. code-block:: bash

   pip install svdep

Basic Usage
-----------

svdep can be used programmatically:

.. code-block:: python

   from svdep import TaskBuildFileCollection, TaskCheckUpToDate, FileCollection
   import json
   import os

   # Build a file collection from root files
   task = TaskBuildFileCollection(
       root_paths=['top.sv', 'pkg.sv'],
       incdirs=['include/', 'src/']
   )
   collection = task.build()

   # Save to JSON
   with open('deps.json', 'w') as f:
       json.dump(collection.to_dict(), f)

   # Later, check if files are up-to-date
   with open('deps.json', 'r') as f:
       collection = FileCollection.from_dict(json.load(f))

   last_build_time = os.path.getmtime('output.bin')
   checker = TaskCheckUpToDate(
       root_files=['top.sv', 'pkg.sv'],
       incdirs=['include/', 'src/']
   )
   if checker.check(collection, last_build_time):
       print("Files are up-to-date, no rebuild needed")
   else:
       print("Files have changed, rebuild required")

Native Implementation
---------------------

svdep includes an optional native C++ implementation that provides improved performance 
for large projects. When the native library is available, it is automatically used 
instead of the pure-Python implementation.

Check if the native implementation is available:

.. code-block:: python

   from svdep import is_native_available, get_native_library_path

   if is_native_available():
       print(f"Using native library: {get_native_library_path()}")
   else:
       print("Using pure-Python implementation")

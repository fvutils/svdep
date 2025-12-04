# SVDep native implementation

The SVDep native implementation provides an implementation of the core 
SVDep algorithm in C++. The existing Python implementation provides
a simplistic SystemVerilog pre-processor that only handles includes.
It uses this to identify the tree of included files, producing a
JSON file that captures the include tree and timestamps for each file.
SVDep runs in two modes:
- Clean: no json exists
- Check: json exists, and the goal is to check whether any files have changed

## Native implementation
Place the C++ implementation in 'cpp'. Implement both a shared library with
a 'C' API that can be loaded and used from Python using the ctypes library.

Implement a full SystemVerilog pre-processor using lex/flex. Use the 
Surelog implementation (which is ANTLR) in reference/Surelog for reference.
See reference/sv_preprocessor.md for the LRM specification of the preprocessor.

The C++ implementation must behave in the same way as the Python implementation,
and must consume and produce the same JSON format. 

The SV processor must interpret all directives, but can omit expansion of 
macro references with parameters for efficiency.

The native implementation of SVDep must not depend on any data in `reference`.

## Build
Add a CMake based build

## Testing
Add pytest tests to tests/unit that load and use the shared library to 
test its operation

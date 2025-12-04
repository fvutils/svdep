API Reference
=============

This section documents the public API of the svdep package.

Main Classes
------------

TaskBuildFileCollection
~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: TaskBuildFileCollection(root_paths, incdirs=None)

   Builds a file collection by scanning root files and their includes.

   :param root_paths: List of paths to root SystemVerilog files to scan.
   :type root_paths: List[str]
   :param incdirs: List of include directories to search for included files.
   :type incdirs: List[str], optional

   .. py:method:: build()

      Scan all root files and their includes, building a complete dependency tree.

      :returns: A FileCollection containing all discovered files and their dependencies.
      :rtype: FileCollection

   **Example:**

   .. code-block:: python

      from svdep import TaskBuildFileCollection

      task = TaskBuildFileCollection(
          root_paths=['top.sv', 'dut.sv'],
          incdirs=['include/', 'rtl/']
      )
      collection = task.build()

TaskCheckUpToDate
~~~~~~~~~~~~~~~~~

.. py:class:: TaskCheckUpToDate(root_files, incdirs=None)

   Checks whether files in a collection are up-to-date relative to a timestamp.

   :param root_files: List of paths to root SystemVerilog files.
   :type root_files: List[str]
   :param incdirs: List of include directories.
   :type incdirs: List[str], optional

   .. py:method:: check(info, timestamp)

      Check if all files in the collection are up-to-date.

      :param info: The file collection to check.
      :type info: FileCollection
      :param timestamp: Reference timestamp (e.g., last build time).
      :type timestamp: float
      :returns: True if all files are up-to-date (not modified since timestamp), False otherwise.
      :rtype: bool

   **Example:**

   .. code-block:: python

      from svdep import TaskCheckUpToDate, FileCollection
      import os

      checker = TaskCheckUpToDate(
          root_files=['top.sv', 'dut.sv'],
          incdirs=['include/']
      )
      
      # Load existing collection
      collection = FileCollection.from_dict(saved_data)
      
      # Check against build output timestamp
      build_time = os.path.getmtime('output.bin')
      is_current = checker.check(collection, build_time)

Data Classes
------------

FileCollection
~~~~~~~~~~~~~~

.. py:class:: FileCollection

   Container for a collection of files and their dependency information.

   .. py:attribute:: root_files
      :type: List[FileInfo]

      List of root file information objects.

   .. py:attribute:: file_info
      :type: Dict[str, FileInfo]

      Dictionary mapping file paths to their FileInfo objects.

   .. py:method:: to_dict()

      Convert the collection to a dictionary suitable for JSON serialization.

      :returns: Dictionary representation of the collection.
      :rtype: dict

   .. py:classmethod:: from_dict(d)

      Create a FileCollection from a dictionary.

      :param d: Dictionary representation of a file collection.
      :type d: dict
      :returns: New FileCollection instance.
      :rtype: FileCollection

FileInfo
~~~~~~~~

.. py:class:: FileInfo

   Information about a single file in the dependency tree.

   .. py:attribute:: name
      :type: str

      Full path to the file.

   .. py:attribute:: timestamp
      :type: int

      File modification timestamp (Unix epoch time).

   .. py:attribute:: includes
      :type: List[str]

      List of paths to files included by this file.

   .. py:method:: to_dict()

      Convert to a dictionary.

      :returns: Dictionary representation.
      :rtype: dict

   .. py:classmethod:: from_dict(d)

      Create a FileInfo from a dictionary.

      :param d: Dictionary representation.
      :type d: dict
      :returns: New FileInfo instance.
      :rtype: FileInfo

Utility Functions
-----------------

.. py:function:: is_native_available()

   Check if the native C++ implementation is available.

   :returns: True if the native library is loaded and available.
   :rtype: bool

.. py:function:: get_native_library_path()

   Get the path to the loaded native library.

   :returns: Path to the native library, or None if not available.
   :rtype: Optional[str]

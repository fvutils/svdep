#****************************************************************************
#* hash_files.py
#*
#* Copyright 2023-2025 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
import hashlib
import logging
from typing import List, Optional, Set
from .task_build_file_collection import TaskBuildFileCollection

_log = logging.getLogger(__name__)


def compute_hash_for_files(files: List[str], incdirs: Optional[List[str]] = None) -> Optional[str]:
    """
    Compute a content-based hash for SystemVerilog/Verilog files including their dependencies.
    
    Args:
        files: List of file paths to hash
        incdirs: List of include directories to search for includes
        
    Returns:
        MD5 hash string of all file contents (including transitive includes), or None on error
    """
    if incdirs is None:
        incdirs = []
    
    try:
        # Build file collection to resolve all includes
        task = TaskBuildFileCollection(root_paths=files, incdirs=incdirs)
        collection = task.build()
        
        # Collect all files in dependency order
        all_files: Set[str] = set()
        
        # Add all root files
        for root_file in collection.root_files:
            _collect_files_recursive(root_file.name, collection.file_info, all_files)
        
        # Sort for deterministic hashing
        sorted_files = sorted(all_files)
        
        # Compute hash over all file contents
        hasher = hashlib.md5()
        for filepath in sorted_files:
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                    hasher.update(filepath.encode('utf-8'))  # Include path in hash
                    hasher.update(content)
            except Exception as e:
                _log.warning(f"Failed to read file {filepath}: {e}")
                return None
        
        return hasher.hexdigest()
        
    except Exception as e:
        _log.error(f"Failed to compute hash for files: {e}")
        return None


def _collect_files_recursive(filepath: str, file_info: dict, collected: Set[str]) -> None:
    """Recursively collect all files including transitive includes."""
    if filepath in collected:
        return
    
    collected.add(filepath)
    
    # Add all includes
    if filepath in file_info:
        info = file_info[filepath]
        for inc_path in info.includes:
            _collect_files_recursive(inc_path, file_info, collected)

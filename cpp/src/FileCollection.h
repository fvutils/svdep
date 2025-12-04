/*
 * FileCollection.h
 *
 * Collection of file information for dependency tracking
 *
 * Copyright 2024 Matthew Ballance and Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may 
 * not use this file except in compliance with the License.  
 * You may obtain a copy of the License at:
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 */
#ifndef FILECOLLECTION_H
#define FILECOLLECTION_H

#include <string>
#include <vector>
#include <unordered_map>
#include "FileInfo.h"

namespace svdep {

class FileCollection {
public:
    FileCollection();
    ~FileCollection();

    // Root files
    std::vector<FileInfo> root_files;
    
    // Map of all file info by path
    std::unordered_map<std::string, FileInfo> file_info;

    // Convert to JSON string
    std::string toJson() const;

    // Load from JSON string
    bool fromJson(const std::string& json);

    // Clear the collection
    void clear();
};

} // namespace svdep

#endif /* FILECOLLECTION_H */

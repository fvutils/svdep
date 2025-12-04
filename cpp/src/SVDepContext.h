/*
 * SVDepContext.h
 *
 * Main context for SVDep operations
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
#ifndef SVDEPCONTEXT_H
#define SVDEPCONTEXT_H

#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include "FileCollection.h"

namespace svdep {

class SVDepContext {
public:
    SVDepContext();
    ~SVDepContext();

    // Add an include directory
    int addIncdir(const std::string& path);

    // Add a root file
    int addRootFile(const std::string& path);

    // Build the file collection
    int build();

    // Get the JSON representation
    const std::string& getJson();

    // Load from JSON
    int loadJson(const std::string& json);

    // Check if up to date
    int checkUpToDate(double lastTimestamp);

    // Get the last error
    const std::string& getError() const;

private:
    // Build file info for a single file
    FileInfo buildFileInfo(const std::string& path);

    // Resolve include path
    std::string resolveInclude(const std::string& filename);

    // Read file contents
    std::string readFile(const std::string& path);

    // Get file modification time
    double getFileTimestamp(const std::string& path);

    // Check if a single file is up to date
    bool checkFileUpToDate(const std::string& path, double lastTimestamp);

    std::vector<std::string> m_incdirs;
    std::vector<std::string> m_rootFiles;
    FileCollection m_collection;
    std::string m_json;
    std::string m_error;

    // Cache for resolved include paths
    std::unordered_map<std::string, std::string> m_includeCache;
};

} // namespace svdep

#endif /* SVDEPCONTEXT_H */

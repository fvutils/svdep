/*
 * SVDepContext.cpp
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
#include "SVDepContext.h"
#include "SVPreprocessor.h"
#include <fstream>
#include <sstream>
#include <sys/stat.h>
#include <cstring>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <libgen.h>
#endif

namespace svdep {

SVDepContext::SVDepContext() {
}

SVDepContext::~SVDepContext() {
}

int SVDepContext::addIncdir(const std::string& path) {
    m_incdirs.push_back(path);
    return 0;
}

int SVDepContext::addRootFile(const std::string& path) {
    m_rootFiles.push_back(path);
    return 0;
}

std::string SVDepContext::readFile(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        m_error = "Failed to open file: " + path;
        return "";
    }
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

double SVDepContext::getFileTimestamp(const std::string& path) {
    struct stat st;
    if (stat(path.c_str(), &st) != 0) {
        return 0;
    }
#ifdef __APPLE__
    return st.st_mtimespec.tv_sec + st.st_mtimespec.tv_nsec / 1e9;
#elif defined(_WIN32)
    return static_cast<double>(st.st_mtime);
#else
    return st.st_mtim.tv_sec + st.st_mtim.tv_nsec / 1e9;
#endif
}

std::string SVDepContext::resolveInclude(const std::string& filename) {
    // Check cache first
    auto it = m_includeCache.find(filename);
    if (it != m_includeCache.end()) {
        return it->second;
    }

    // Search in include directories
    for (const auto& incdir : m_incdirs) {
        std::string fullPath = incdir + "/" + filename;
        struct stat st;
        if (stat(fullPath.c_str(), &st) == 0) {
            m_includeCache[filename] = fullPath;
            return fullPath;
        }
    }

    return "";
}

static std::string getDirname(const std::string& path) {
    size_t pos = path.find_last_of("/\\");
    if (pos == std::string::npos) {
        return ".";
    }
    return path.substr(0, pos);
}

FileInfo SVDepContext::buildFileInfo(const std::string& path) {
    // Check if already processed
    auto it = m_collection.file_info.find(path);
    if (it != m_collection.file_info.end()) {
        return it->second;
    }

    FileInfo info;
    info.name = path;
    info.timestamp = getFileTimestamp(path);

    // Add to collection first to handle circular includes
    m_collection.file_info[path] = info;

    // Read and process the file
    std::string content = readFile(path);
    if (content.empty() && !m_error.empty()) {
        return info;
    }

    SVPreprocessor pp;
    pp.setInput(content, path);
    pp.process();

    // Process includes
    const auto& includes = pp.getIncludes();
    for (const auto& inc : includes) {
        std::string incPath = resolveInclude(inc);
        if (!incPath.empty()) {
            // Add directory of included file to search path
            std::string incDir = getDirname(incPath);
            bool found = false;
            for (const auto& dir : m_incdirs) {
                if (dir == incDir) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                m_incdirs.push_back(incDir);
            }

            // Recursively process include
            buildFileInfo(incPath);
            info.includes.push_back(incPath);
        }
    }

    // Update the stored info with includes
    m_collection.file_info[path] = info;
    return info;
}

int SVDepContext::build() {
    m_collection.clear();
    m_error.clear();

    for (const auto& rootPath : m_rootFiles) {
        // Add directory of root file to search path
        std::string rootDir = getDirname(rootPath);
        bool found = false;
        for (const auto& dir : m_incdirs) {
            if (dir == rootDir) {
                found = true;
                break;
            }
        }
        if (!found) {
            m_incdirs.push_back(rootDir);
        }

        FileInfo info = buildFileInfo(rootPath);
        if (!m_error.empty()) {
            return -1;
        }
        m_collection.root_files.push_back(info);
    }

    return 0;
}

const std::string& SVDepContext::getJson() {
    m_json = m_collection.toJson();
    return m_json;
}

int SVDepContext::loadJson(const std::string& json) {
    m_collection.clear();
    if (!m_collection.fromJson(json)) {
        m_error = "Failed to parse JSON";
        return -1;
    }
    return 0;
}

bool SVDepContext::checkFileUpToDate(const std::string& path, double lastTimestamp) {
    auto it = m_collection.file_info.find(path);
    if (it == m_collection.file_info.end()) {
        return false;
    }

    FileInfo& info = it->second;
    if (info.checked) {
        return true;
    }
    info.checked = true;

    // Check if file still exists and timestamp matches
    double currentTs = getFileTimestamp(path);
    if (currentTs == 0) {
        return false; // File doesn't exist
    }

    if (currentTs > lastTimestamp) {
        return false; // File was modified after last check
    }

    // Check all includes
    for (const auto& incPath : info.includes) {
        if (!checkFileUpToDate(incPath, lastTimestamp)) {
            return false;
        }
    }

    return true;
}

int SVDepContext::checkUpToDate(double lastTimestamp) {
    // Check that root files match
    if (m_rootFiles.size() != m_collection.root_files.size()) {
        return 0; // Different number of root files
    }

    // Reset checked flags
    for (auto& kv : m_collection.file_info) {
        kv.second.checked = false;
    }

    // Check each root file
    for (size_t i = 0; i < m_rootFiles.size(); i++) {
        if (m_rootFiles[i] != m_collection.root_files[i].name) {
            return 0; // Root file list changed
        }
        if (!checkFileUpToDate(m_rootFiles[i], lastTimestamp)) {
            return 0;
        }
    }

    return 1; // Up to date
}

const std::string& SVDepContext::getError() const {
    return m_error;
}

} // namespace svdep

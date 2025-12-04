/*
 * FileCollection.cpp
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
#include "FileCollection.h"
#include <sstream>
#include <iomanip>
#include <cstring>

namespace svdep {

FileCollection::FileCollection() {
}

FileCollection::~FileCollection() {
}

void FileCollection::clear() {
    root_files.clear();
    file_info.clear();
}

// Simple JSON escape
static std::string escapeJson(const std::string& s) {
    std::ostringstream o;
    for (char c : s) {
        switch (c) {
            case '"': o << "\\\""; break;
            case '\\': o << "\\\\"; break;
            case '\b': o << "\\b"; break;
            case '\f': o << "\\f"; break;
            case '\n': o << "\\n"; break;
            case '\r': o << "\\r"; break;
            case '\t': o << "\\t"; break;
            default:
                if ('\x00' <= c && c <= '\x1f') {
                    o << "\\u" << std::hex << std::setw(4) << std::setfill('0') << (int)c;
                } else {
                    o << c;
                }
        }
    }
    return o.str();
}

static void writeFileInfo(std::ostringstream& os, const FileInfo& info) {
    os << "{";
    os << "\"name\": \"" << escapeJson(info.name) << "\", ";
    os << "\"timestamp\": " << std::fixed << std::setprecision(6) << info.timestamp << ", ";
    os << "\"includes\": [";
    for (size_t i = 0; i < info.includes.size(); i++) {
        if (i > 0) os << ", ";
        os << "\"" << escapeJson(info.includes[i]) << "\"";
    }
    os << "]";
    os << "}";
}

std::string FileCollection::toJson() const {
    std::ostringstream os;
    os << "{";
    
    // root_files
    os << "\"root_files\": [";
    for (size_t i = 0; i < root_files.size(); i++) {
        if (i > 0) os << ", ";
        writeFileInfo(os, root_files[i]);
    }
    os << "], ";
    
    // file_info
    os << "\"file_info\": {";
    bool first = true;
    for (const auto& kv : file_info) {
        if (!first) os << ", ";
        first = false;
        os << "\"" << escapeJson(kv.first) << "\": ";
        writeFileInfo(os, kv.second);
    }
    os << "}";
    
    os << "}";
    return os.str();
}

// Simple JSON parser helpers
class JsonParser {
public:
    JsonParser(const std::string& json) : m_json(json), m_pos(0) {}

    void skipWhitespace() {
        while (m_pos < m_json.size() && 
               (m_json[m_pos] == ' ' || m_json[m_pos] == '\t' || 
                m_json[m_pos] == '\n' || m_json[m_pos] == '\r')) {
            m_pos++;
        }
    }

    bool match(char c) {
        skipWhitespace();
        if (m_pos < m_json.size() && m_json[m_pos] == c) {
            m_pos++;
            return true;
        }
        return false;
    }

    std::string parseString() {
        skipWhitespace();
        if (m_pos >= m_json.size() || m_json[m_pos] != '"') return "";
        m_pos++; // skip opening quote
        
        std::string result;
        while (m_pos < m_json.size()) {
            char c = m_json[m_pos++];
            if (c == '"') break;
            if (c == '\\' && m_pos < m_json.size()) {
                char escaped = m_json[m_pos++];
                switch (escaped) {
                    case 'n': result += '\n'; break;
                    case 't': result += '\t'; break;
                    case 'r': result += '\r'; break;
                    case '\\': result += '\\'; break;
                    case '"': result += '"'; break;
                    default: result += escaped; break;
                }
            } else {
                result += c;
            }
        }
        return result;
    }

    double parseNumber() {
        skipWhitespace();
        size_t start = m_pos;
        bool hasDecimal = false;
        
        if (m_pos < m_json.size() && m_json[m_pos] == '-') m_pos++;
        while (m_pos < m_json.size() && 
               (std::isdigit(m_json[m_pos]) || m_json[m_pos] == '.' || 
                m_json[m_pos] == 'e' || m_json[m_pos] == 'E' ||
                m_json[m_pos] == '+' || m_json[m_pos] == '-')) {
            m_pos++;
        }
        
        std::string numStr = m_json.substr(start, m_pos - start);
        return std::stod(numStr);
    }

    FileInfo parseFileInfo() {
        FileInfo info;
        if (!match('{')) return info;
        
        while (m_pos < m_json.size()) {
            skipWhitespace();
            if (m_json[m_pos] == '}') {
                m_pos++;
                break;
            }
            
            std::string key = parseString();
            if (!match(':')) break;
            
            if (key == "name") {
                info.name = parseString();
            } else if (key == "timestamp") {
                info.timestamp = parseNumber();
            } else if (key == "includes") {
                if (match('[')) {
                    while (m_pos < m_json.size()) {
                        skipWhitespace();
                        if (m_json[m_pos] == ']') {
                            m_pos++;
                            break;
                        }
                        info.includes.push_back(parseString());
                        match(',');
                    }
                }
            }
            
            match(',');
        }
        
        return info;
    }

    bool parse(FileCollection& collection) {
        if (!match('{')) return false;
        
        while (m_pos < m_json.size()) {
            skipWhitespace();
            if (m_json[m_pos] == '}') {
                m_pos++;
                break;
            }
            
            std::string key = parseString();
            if (!match(':')) break;
            
            if (key == "root_files") {
                if (match('[')) {
                    while (m_pos < m_json.size()) {
                        skipWhitespace();
                        if (m_json[m_pos] == ']') {
                            m_pos++;
                            break;
                        }
                        collection.root_files.push_back(parseFileInfo());
                        match(',');
                    }
                }
            } else if (key == "file_info") {
                if (match('{')) {
                    while (m_pos < m_json.size()) {
                        skipWhitespace();
                        if (m_json[m_pos] == '}') {
                            m_pos++;
                            break;
                        }
                        std::string path = parseString();
                        if (!match(':')) break;
                        collection.file_info[path] = parseFileInfo();
                        match(',');
                    }
                }
            }
            
            match(',');
        }
        
        return true;
    }

private:
    const std::string& m_json;
    size_t m_pos;
};

bool FileCollection::fromJson(const std::string& json) {
    clear();
    JsonParser parser(json);
    return parser.parse(*this);
}

} // namespace svdep

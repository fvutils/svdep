/*
 * SVPreprocessor.cpp
 *
 * SystemVerilog Preprocessor Implementation
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
#include "SVPreprocessor.h"
#include <cctype>
#include <stdexcept>

namespace svdep {

SVPreprocessor::SVPreprocessor()
    : m_pos(0), m_line(1), m_column(1), m_hasPeeked(false) {
}

SVPreprocessor::~SVPreprocessor() {
}

void SVPreprocessor::setInput(const std::string& content, const std::string& filename) {
    m_content = content;
    m_filename = filename;
    m_pos = 0;
    m_line = 1;
    m_column = 1;
    m_hasPeeked = false;
    m_includes.clear();
    m_condStack.clear();
}

void SVPreprocessor::setIncludeCallback(IncludeCallback callback) {
    m_includeCallback = callback;
}

Token SVPreprocessor::nextToken() {
    if (m_hasPeeked) {
        m_hasPeeked = false;
        return m_peeked;
    }
    return scanToken();
}

Token SVPreprocessor::peekToken() {
    if (!m_hasPeeked) {
        m_peeked = scanToken();
        m_hasPeeked = true;
    }
    return m_peeked;
}

const std::vector<std::string>& SVPreprocessor::getIncludes() const {
    return m_includes;
}

void SVPreprocessor::process() {
    while (!isAtEnd()) {
        Token tok = nextToken();
        if (tok.type == TokenType::END_OF_FILE) {
            break;
        }
    }
}

void SVPreprocessor::defineMacro(const std::string& name, const std::string& value) {
    m_macros[name] = value;
}

void SVPreprocessor::undefineMacro(const std::string& name) {
    m_macros.erase(name);
}

bool SVPreprocessor::isMacroDefined(const std::string& name) const {
    return m_macros.find(name) != m_macros.end();
}

char SVPreprocessor::peek() const {
    if (isAtEnd()) return '\0';
    return m_content[m_pos];
}

char SVPreprocessor::advance() {
    if (isAtEnd()) return '\0';
    char c = m_content[m_pos++];
    if (c == '\n') {
        m_line++;
        m_column = 1;
    } else {
        m_column++;
    }
    return c;
}

bool SVPreprocessor::match(char expected) {
    if (isAtEnd() || m_content[m_pos] != expected) return false;
    advance();
    return true;
}

bool SVPreprocessor::isAtEnd() const {
    return m_pos >= m_content.size();
}

void SVPreprocessor::skipWhitespace() {
    while (!isAtEnd()) {
        char c = peek();
        if (c == ' ' || c == '\t' || c == '\r') {
            advance();
        } else {
            break;
        }
    }
}

void SVPreprocessor::skipWhitespaceNotNewline() {
    while (!isAtEnd()) {
        char c = peek();
        if (c == ' ' || c == '\t') {
            advance();
        } else {
            break;
        }
    }
}

Token SVPreprocessor::makeToken(TokenType type, const std::string& value) {
    Token tok;
    tok.type = type;
    tok.value = value;
    tok.line = m_line;
    tok.column = m_column;
    return tok;
}

Token SVPreprocessor::scanToken() {
    // Skip whitespace but track newlines
    while (!isAtEnd()) {
        char c = peek();
        if (c == ' ' || c == '\t' || c == '\r') {
            advance();
        } else if (c == '\n') {
            advance();
            // Continue - don't return newline token
        } else {
            break;
        }
    }

    if (isAtEnd()) {
        return makeToken(TokenType::END_OF_FILE, "");
    }

    char c = peek();

    // Comments
    if (c == '/') {
        if (m_pos + 1 < m_content.size()) {
            char next = m_content[m_pos + 1];
            if (next == '/') {
                return scanLineComment();
            } else if (next == '*') {
                return scanBlockComment();
            }
        }
    }

    // Directive
    if (c == '`') {
        return scanDirective();
    }

    // String
    if (c == '"') {
        return scanString();
    }

    // Number
    if (std::isdigit(c)) {
        return scanNumber();
    }

    // Identifier
    if (std::isalpha(c) || c == '_' || c == '$') {
        return scanIdentifier();
    }

    // Single character operators/punctuation
    advance();
    return makeToken(TokenType::OPERATOR, std::string(1, c));
}

Token SVPreprocessor::scanIdentifier() {
    std::string value;
    while (!isAtEnd()) {
        char c = peek();
        if (std::isalnum(c) || c == '_' || c == '$') {
            value += advance();
        } else {
            break;
        }
    }
    return makeToken(TokenType::IDENTIFIER, value);
}

Token SVPreprocessor::scanString() {
    std::string value;
    advance(); // consume opening "
    
    while (!isAtEnd()) {
        char c = peek();
        if (c == '"') {
            advance(); // consume closing "
            break;
        } else if (c == '\\') {
            advance();
            if (!isAtEnd()) {
                char escaped = advance();
                switch (escaped) {
                    case 'n': value += '\n'; break;
                    case 't': value += '\t'; break;
                    case 'r': value += '\r'; break;
                    case '\\': value += '\\'; break;
                    case '"': value += '"'; break;
                    default: value += escaped; break;
                }
            }
        } else if (c == '\n') {
            // Unterminated string
            break;
        } else {
            value += advance();
        }
    }
    return makeToken(TokenType::STRING, value);
}

Token SVPreprocessor::scanNumber() {
    std::string value;
    while (!isAtEnd()) {
        char c = peek();
        if (std::isdigit(c) || c == '_' || c == '\'') {
            value += advance();
            // Handle base specifier like 'h, 'b, 'd, 'o
            if (c == '\'' && !isAtEnd()) {
                c = peek();
                if (c == 'h' || c == 'H' || c == 'b' || c == 'B' ||
                    c == 'd' || c == 'D' || c == 'o' || c == 'O' ||
                    c == 's' || c == 'S') {
                    value += advance();
                }
            }
        } else if (std::isxdigit(c) || c == 'x' || c == 'X' || c == 'z' || c == 'Z' || c == '?') {
            value += advance();
        } else {
            break;
        }
    }
    return makeToken(TokenType::NUMBER, value);
}

Token SVPreprocessor::scanDirective() {
    advance(); // consume `
    
    std::string name;
    while (!isAtEnd()) {
        char c = peek();
        if (std::isalnum(c) || c == '_') {
            name += advance();
        } else {
            break;
        }
    }

    // Handle directive if we're in active code
    if (!name.empty()) {
        handleDirective(name);
    }

    return makeToken(TokenType::DIRECTIVE, name);
}

Token SVPreprocessor::scanLineComment() {
    std::string value;
    advance(); // consume first /
    advance(); // consume second /
    
    while (!isAtEnd()) {
        char c = peek();
        if (c == '\n') {
            advance();
            break;
        }
        value += advance();
    }
    return makeToken(TokenType::COMMENT_LINE, value);
}

Token SVPreprocessor::scanBlockComment() {
    std::string value;
    advance(); // consume /
    advance(); // consume *
    
    while (!isAtEnd()) {
        if (peek() == '*' && m_pos + 1 < m_content.size() && m_content[m_pos + 1] == '/') {
            advance(); // consume *
            advance(); // consume /
            break;
        }
        value += advance();
    }
    return makeToken(TokenType::COMMENT_BLOCK, value);
}

bool SVPreprocessor::isActive() const {
    if (m_condStack.empty()) return true;
    return m_condStack.back().active;
}

void SVPreprocessor::handleDirective(const std::string& directive) {
    if (directive == "include") {
        if (isActive()) {
            handleInclude();
        } else {
            skipToEndOfLine();
        }
    } else if (directive == "define") {
        if (isActive()) {
            handleDefine();
        } else {
            skipToEndOfLine();
        }
    } else if (directive == "undef") {
        if (isActive()) {
            handleUndef();
        } else {
            skipToEndOfLine();
        }
    } else if (directive == "ifdef") {
        handleIfdef(false);
    } else if (directive == "ifndef") {
        handleIfdef(true);
    } else if (directive == "elsif" || directive == "elseif") {
        handleElsif();
    } else if (directive == "else") {
        handleElse();
    } else if (directive == "endif") {
        handleEndif();
    } else {
        // Other directives (timescale, resetall, etc.) - skip to end of line if inactive
        if (!isActive()) {
            skipToEndOfLine();
        }
    }
}

void SVPreprocessor::handleInclude() {
    skipWhitespaceNotNewline();
    
    std::string filename;
    char c = peek();
    
    if (c == '"') {
        // "filename"
        advance();
        while (!isAtEnd()) {
            c = peek();
            if (c == '"') {
                advance();
                break;
            } else if (c == '\n') {
                break;
            }
            filename += advance();
        }
    } else if (c == '<') {
        // <filename> - also valid in some tools
        advance();
        while (!isAtEnd()) {
            c = peek();
            if (c == '>') {
                advance();
                break;
            } else if (c == '\n') {
                break;
            }
            filename += advance();
        }
    } else if (c == '`') {
        // Could be a macro that expands to a filename - skip for now
        skipToEndOfLine();
        return;
    }

    if (!filename.empty()) {
        m_includes.push_back(filename);
    }
}

void SVPreprocessor::handleDefine() {
    skipWhitespaceNotNewline();
    
    std::string name = parseIdentifier();
    if (name.empty()) {
        skipToEndOfLine();
        return;
    }

    // Check for macro with parameters - we'll store but not fully process
    std::string value;
    char c = peek();
    
    if (c == '(') {
        // Macro with parameters - skip parameters for now
        while (!isAtEnd() && peek() != ')') {
            advance();
        }
        if (!isAtEnd()) advance(); // consume )
        skipWhitespaceNotNewline();
    } else {
        skipWhitespaceNotNewline();
    }

    // Collect macro body until end of line (handling line continuations)
    while (!isAtEnd()) {
        c = peek();
        if (c == '\n') {
            advance();
            break;
        } else if (c == '\\') {
            // Check for line continuation
            if (m_pos + 1 < m_content.size() && m_content[m_pos + 1] == '\n') {
                advance(); // consume backslash
                advance(); // consume newline
                continue;
            } else if (m_pos + 2 < m_content.size() && 
                       m_content[m_pos + 1] == '\r' && m_content[m_pos + 2] == '\n') {
                advance(); // consume backslash
                advance(); // consume \r
                advance(); // consume \n
                continue;
            }
        }
        value += advance();
    }

    // Trim trailing whitespace
    while (!value.empty() && (value.back() == ' ' || value.back() == '\t')) {
        value.pop_back();
    }

    m_macros[name] = value.empty() ? "1" : value;
}

void SVPreprocessor::handleUndef() {
    skipWhitespaceNotNewline();
    std::string name = parseIdentifier();
    if (!name.empty()) {
        m_macros.erase(name);
    }
    skipToEndOfLine();
}

void SVPreprocessor::handleIfdef(bool invert) {
    skipWhitespaceNotNewline();
    std::string name = parseIdentifier();
    
    bool defined = isMacroDefined(name);
    if (invert) defined = !defined;

    CondState state;
    state.seen_true = defined && isActive();
    state.active = state.seen_true;
    state.in_else = false;
    
    m_condStack.push_back(state);
    skipToEndOfLine();
}

void SVPreprocessor::handleElsif() {
    if (m_condStack.empty()) {
        // Error: elsif without ifdef
        skipToEndOfLine();
        return;
    }

    CondState& state = m_condStack.back();
    if (state.in_else) {
        // Error: elsif after else
        skipToEndOfLine();
        return;
    }

    skipWhitespaceNotNewline();
    std::string name = parseIdentifier();
    
    bool defined = isMacroDefined(name);
    
    // Parent must be active, and we haven't seen a true branch yet
    bool parent_active = m_condStack.size() == 1 || 
        (m_condStack.size() > 1 && m_condStack[m_condStack.size() - 2].active);
    
    if (!state.seen_true && defined && parent_active) {
        state.active = true;
        state.seen_true = true;
    } else {
        state.active = false;
    }
    
    skipToEndOfLine();
}

void SVPreprocessor::handleElse() {
    if (m_condStack.empty()) {
        // Error: else without ifdef
        return;
    }

    CondState& state = m_condStack.back();
    if (state.in_else) {
        // Error: multiple else
        return;
    }

    state.in_else = true;
    
    // Parent must be active, and we haven't seen a true branch yet
    bool parent_active = m_condStack.size() == 1 || 
        (m_condStack.size() > 1 && m_condStack[m_condStack.size() - 2].active);
    
    state.active = !state.seen_true && parent_active;
}

void SVPreprocessor::handleEndif() {
    if (!m_condStack.empty()) {
        m_condStack.pop_back();
    }
}

std::string SVPreprocessor::parseIdentifier() {
    std::string name;
    while (!isAtEnd()) {
        char c = peek();
        if (std::isalnum(c) || c == '_') {
            name += advance();
        } else {
            break;
        }
    }
    return name;
}

std::string SVPreprocessor::parseString() {
    if (peek() != '"') return "";
    advance();
    
    std::string value;
    while (!isAtEnd()) {
        char c = peek();
        if (c == '"') {
            advance();
            break;
        } else if (c == '\\') {
            advance();
            if (!isAtEnd()) value += advance();
        } else if (c == '\n') {
            break;
        } else {
            value += advance();
        }
    }
    return value;
}

void SVPreprocessor::skipToEndOfLine() {
    while (!isAtEnd()) {
        char c = peek();
        if (c == '\n') {
            advance();
            break;
        } else if (c == '\\') {
            // Handle line continuation
            if (m_pos + 1 < m_content.size() && m_content[m_pos + 1] == '\n') {
                advance();
                advance();
                continue;
            } else if (m_pos + 2 < m_content.size() && 
                       m_content[m_pos + 1] == '\r' && m_content[m_pos + 2] == '\n') {
                advance();
                advance();
                advance();
                continue;
            }
        }
        advance();
    }
}

} // namespace svdep

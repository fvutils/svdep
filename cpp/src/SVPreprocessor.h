/*
 * SVPreprocessor.h
 *
 * SystemVerilog Preprocessor Lexer
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
#ifndef SVPREPROCESSOR_H
#define SVPREPROCESSOR_H

#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <functional>

namespace svdep {

enum class TokenType {
    END_OF_FILE,
    IDENTIFIER,
    STRING,
    NUMBER,
    DIRECTIVE,
    WHITESPACE,
    NEWLINE,
    COMMENT_LINE,
    COMMENT_BLOCK,
    OPERATOR,
    UNKNOWN
};

struct Token {
    TokenType type;
    std::string value;
    int line;
    int column;
};

/**
 * SystemVerilog Preprocessor
 * 
 * Implements lexing and directive interpretation for SV preprocessor.
 * Directives supported:
 * - `include
 * - `define / `undef
 * - `ifdef / `ifndef / `elsif / `else / `endif
 * - `timescale, `resetall, `celldefine, `endcelldefine, etc.
 */
class SVPreprocessor {
public:
    using IncludeCallback = std::function<std::string(const std::string&)>;

    SVPreprocessor();
    ~SVPreprocessor();

    // Set the input source
    void setInput(const std::string& content, const std::string& filename = "");

    // Set callback for resolving include files
    void setIncludeCallback(IncludeCallback callback);

    // Get next token
    Token nextToken();

    // Peek at next token without consuming
    Token peekToken();

    // Get all include files found during processing
    const std::vector<std::string>& getIncludes() const;

    // Process the entire input, collecting includes
    void process();

    // Define a macro
    void defineMacro(const std::string& name, const std::string& value = "1");

    // Undefine a macro
    void undefineMacro(const std::string& name);

    // Check if macro is defined
    bool isMacroDefined(const std::string& name) const;

private:
    std::string m_content;
    std::string m_filename;
    size_t m_pos;
    int m_line;
    int m_column;
    
    Token m_peeked;
    bool m_hasPeeked;

    std::vector<std::string> m_includes;
    std::unordered_map<std::string, std::string> m_macros;
    
    // Conditional compilation stack
    struct CondState {
        bool active;      // Is this branch active?
        bool seen_true;   // Have we seen a true condition in this if/elsif chain?
        bool in_else;     // Are we in the else branch?
    };
    std::vector<CondState> m_condStack;

    IncludeCallback m_includeCallback;

    // Lexer helpers
    char peek() const;
    char advance();
    bool match(char expected);
    bool isAtEnd() const;
    void skipWhitespace();
    Token makeToken(TokenType type, const std::string& value);
    
    // Token scanning
    Token scanToken();
    Token scanIdentifier();
    Token scanString();
    Token scanNumber();
    Token scanDirective();
    Token scanLineComment();
    Token scanBlockComment();
    
    // Directive handling
    void handleDirective(const std::string& directive);
    void handleInclude();
    void handleDefine();
    void handleUndef();
    void handleIfdef(bool invert);
    void handleElsif();
    void handleElse();
    void handleEndif();
    
    // Conditional compilation
    bool isActive() const;
    
    // Parse helpers
    std::string parseString();
    std::string parseIdentifier();
    void skipToEndOfLine();
    void skipWhitespaceNotNewline();
};

} // namespace svdep

#endif /* SVPREPROCESSOR_H */

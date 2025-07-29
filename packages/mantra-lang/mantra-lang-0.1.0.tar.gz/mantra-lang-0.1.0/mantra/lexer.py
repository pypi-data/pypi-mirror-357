from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    # Core tokens
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    
    # Sanskrit keywords
    KRIYA = "kriya"
    STHANA = "sthana"
    YADI = "yadi"
    ATHAVA = "athava"
    PUNAR = "punar"
    GATI = "gati"
    SATY = "saty"
    ASATY = "asaty"
    SHUNYA = "shunya"
    
    # 🔥 NEW: Advanced Sanskrit keywords
    YANTRA = "yantra"      # GUI elements
    SHAKTI = "shakti"      # Power expressions  
    SUTRA = "sutra"        # Function composition
    RAGA = "raga"          # Data flow
    MANDAL = "mandal"      # Circular data
    SEVA = "seva"          # Service/API
    
    # Operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    ASSIGN = "="
    EQUALS = "=="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    DOT = "."              # For property access
    
    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["         # For arrays
    RBRACKET = "]"
    COMMA = ","
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int = 1

class SimpleLexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        
        self.keywords = {
            'kriya': TokenType.KRIYA,
            'sthana': TokenType.STHANA,
            'yadi': TokenType.YADI,
            'athava': TokenType.ATHAVA,
            'punar': TokenType.PUNAR,
            'gati': TokenType.GATI,
            'saty': TokenType.SATY,
            'asaty': TokenType.ASATY,
            'shunya': TokenType.SHUNYA,
            # 🔥 NEW: Advanced keywords
            'yantra': TokenType.YANTRA,
            'shakti': TokenType.SHAKTI,
            'sutra': TokenType.SUTRA,
            'raga': TokenType.RAGA,
            'mandal': TokenType.MANDAL,
            'seva': TokenType.SEVA,
        }
    
    def current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def peek_char(self):
        if self.pos + 1 >= len(self.text):
            return None
        return self.text[self.pos + 1]
    
    def advance(self):
        if self.pos < len(self.text) and self.text[self.pos] == '\n':
            self.line += 1
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self):
        num_str = ''
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            num_str += self.current_char()
            self.advance()
        return num_str
    
    def read_string(self):
        quote = self.current_char()
        self.advance()
        string_val = ''
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\' and self.peek_char() == quote:
                # Handle escaped quotes
                self.advance()
                string_val += quote
                self.advance()
            else:
                string_val += self.current_char()
                self.advance()
        if self.current_char() == quote:
            self.advance()
        return string_val
    
    def read_identifier(self):
        identifier = ''
        # Allow Unicode characters for Sanskrit
        while self.current_char() and (self.current_char().isalnum() or 
                                     self.current_char() == '_' or 
                                     ord(self.current_char()) > 127):
            identifier += self.current_char()
            self.advance()
        return identifier
    
    def tokenize(self):
        tokens = []
        
        while self.pos < len(self.text):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # Comments
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # Newlines
            if self.current_char() == '\n':
                tokens.append(Token(TokenType.NEWLINE, '\n', self.line))
                self.advance()
                continue
            
            # Numbers
            if self.current_char().isdigit():
                tokens.append(Token(TokenType.NUMBER, self.read_number(), self.line))
                continue
            
            # Strings
            if self.current_char() in '"\'':
                tokens.append(Token(TokenType.STRING, self.read_string(), self.line))
                continue
            
            # Two-character operators
            if self.current_char() == '=' and self.peek_char() == '=':
                tokens.append(Token(TokenType.EQUALS, '==', self.line))
                self.advance()
                self.advance()
                continue
            
            if self.current_char() == '!' and self.peek_char() == '=':
                tokens.append(Token(TokenType.NOT_EQUALS, '!=', self.line))
                self.advance()
                self.advance()
                continue
            
            if self.current_char() == '<' and self.peek_char() == '=':
                tokens.append(Token(TokenType.LESS_EQUAL, '<=', self.line))
                self.advance()
                self.advance()
                continue
            
            if self.current_char() == '>' and self.peek_char() == '=':
                tokens.append(Token(TokenType.GREATER_EQUAL, '>=', self.line))
                self.advance()
                self.advance()
                continue
            
            # Single character operators
            single_chars = {
                '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE, '=': TokenType.ASSIGN, '<': TokenType.LESS_THAN,
                '>': TokenType.GREATER_THAN, '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '{': TokenType.LBRACE, '}': TokenType.RBRACE, ',': TokenType.COMMA,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET, '.': TokenType.DOT
            }
            
            if self.current_char() in single_chars:
                tokens.append(Token(single_chars[self.current_char()], self.current_char(), self.line))
                self.advance()
                continue
            
            # Identifiers and keywords (including Unicode)
            if self.current_char().isalpha() or self.current_char() == '_' or ord(self.current_char()) > 127:
                identifier = self.read_identifier()
                token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                tokens.append(Token(token_type, identifier, self.line))
                continue
            
            # Skip unknown characters
            print(f"Warning: Unknown character '{self.current_char()}' at line {self.line}")
            self.advance()
        
        tokens.append(Token(TokenType.EOF, '', self.line))
        return tokens
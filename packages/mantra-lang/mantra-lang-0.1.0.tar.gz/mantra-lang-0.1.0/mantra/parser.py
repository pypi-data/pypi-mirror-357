from typing import List, Optional
from .lexer import Token, TokenType
from .ast_nodes import *

class SimpleParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def match(self, *token_types):
        return self.current_token().type in token_types
    
    def consume(self, token_type):
        if self.current_token().type == token_type:
            token = self.current_token()
            self.advance()
            return token
        raise SyntaxError(f"Expected {token_type}, got {self.current_token().type} at line {self.current_token().line}")
    
    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse(self):
        statements = []
        self.skip_newlines()
        
        while not self.match(TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return ProgramNode(statements)
    
    def parse_statement(self):
        self.skip_newlines()
        
        # Basic statements
        if self.match(TokenType.STHANA):
            return self.parse_variable_declaration()
        elif self.match(TokenType.KRIYA):
            return self.parse_function_definition()
        elif self.match(TokenType.YADI):
            return self.parse_if_statement()
        elif self.match(TokenType.PUNAR):
            return self.parse_loop()
        elif self.match(TokenType.GATI):
            return self.parse_return()
        
        # 🔥 NEW: Advanced statements
        elif self.match(TokenType.YANTRA):
            return self.parse_yantra()
        elif self.match(TokenType.SHAKTI):
            return self.parse_shakti()
        elif self.match(TokenType.SUTRA):
            return self.parse_sutra()
        elif self.match(TokenType.RAGA):
            return self.parse_raga()
        elif self.match(TokenType.MANDAL):
            return self.parse_mandal()
        elif self.match(TokenType.SEVA):
            return self.parse_seva()
        
        else:
            # Expression or assignment
            expr = self.parse_expression()
            if self.match(TokenType.ASSIGN):
                if isinstance(expr, IdentifierNode):
                    self.advance()
                    value = self.parse_expression()
                    return AssignmentNode(expr.name, value)
            return expr
    
    def parse_variable_declaration(self):
        self.consume(TokenType.STHANA)
        name = self.consume(TokenType.IDENTIFIER).value
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            return VariableDeclarationNode(name, value)
        return VariableDeclarationNode(name)
    
    def parse_function_definition(self):
        self.consume(TokenType.KRIYA)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LPAREN)
        
        params = []
        while not self.match(TokenType.RPAREN):
            params.append(self.consume(TokenType.IDENTIFIER).value)
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.LBRACE)
        
        body = []
        while not self.match(TokenType.RBRACE):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.RBRACE)
        return FunctionDefNode(name, params, body)
    
    def parse_if_statement(self):
        self.consume(TokenType.YADI)
        condition = self.parse_expression()
        self.consume(TokenType.LBRACE)
        
        then_branch = []
        while not self.match(TokenType.RBRACE):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            stmt = self.parse_statement()
            if stmt:
                then_branch.append(stmt)
        
        self.consume(TokenType.RBRACE)
        
        else_branch = None
        if self.match(TokenType.ATHAVA):
            self.advance()
            if self.match(TokenType.YADI):
                # else if
                else_branch = [self.parse_if_statement()]
            else:
                self.consume(TokenType.LBRACE)
                else_branch = []
                while not self.match(TokenType.RBRACE):
                    self.skip_newlines()
                    if self.match(TokenType.RBRACE):
                        break
                    stmt = self.parse_statement()
                    if stmt:
                        else_branch.append(stmt)
                self.consume(TokenType.RBRACE)
        
        return IfNode(condition, then_branch, else_branch)
    
    def parse_loop(self):
        self.consume(TokenType.PUNAR)
        condition = self.parse_expression()
        self.consume(TokenType.LBRACE)
        
        body = []
        while not self.match(TokenType.RBRACE):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.RBRACE)
        return LoopNode(condition, body)
    
    def parse_return(self):
        self.consume(TokenType.GATI)
        value = None
        if not self.match(TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            value = self.parse_expression()
        return ReturnNode(value)
    
    # 🔥 NEW: Advanced parsing methods
    
    def parse_yantra(self):
        """Parse GUI element creation"""
        self.consume(TokenType.YANTRA)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.ASSIGN)
        
        element_type = self.consume(TokenType.STRING).value
        properties = {}
        
        if self.match(TokenType.LPAREN):
            self.advance()
            while not self.match(TokenType.RPAREN):
                prop_name = self.consume(TokenType.IDENTIFIER).value
                self.consume(TokenType.ASSIGN)
                prop_value = self.parse_expression()
                properties[prop_name] = prop_value
                
                if self.match(TokenType.COMMA):
                    self.advance()
            self.consume(TokenType.RPAREN)
        
        return YantraDeclarationNode(name, element_type, properties)
    
    def parse_shakti(self):
        """Parse power expression"""
        self.consume(TokenType.SHAKTI)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.ASSIGN)
        
        expr_type = self.consume(TokenType.STRING).value
        properties = {}
        
        if self.match(TokenType.LPAREN):
            self.advance()
            while not self.match(TokenType.RPAREN):
                prop_name = self.consume(TokenType.IDENTIFIER).value
                self.consume(TokenType.ASSIGN)
                prop_value = self.parse_expression()
                properties[prop_name] = prop_value
                
                if self.match(TokenType.COMMA):
                    self.advance()
            self.consume(TokenType.RPAREN)
        
        return ShaktiDeclarationNode(name, expr_type, properties)
    
    def parse_sutra(self):
        """Parse function composition"""
        self.consume(TokenType.SUTRA)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.ASSIGN)
        self.consume(TokenType.LBRACKET)
        
        functions = []
        while not self.match(TokenType.RBRACKET):
            functions.append(self.parse_expression())
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.consume(TokenType.RBRACKET)
        return SutraDeclarationNode(name, functions)
    
    def parse_raga(self):
        """Parse data flow"""
        self.consume(TokenType.RAGA)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.ASSIGN)
        
        source = self.parse_expression()
        transformations = []
        
        # Handle chained transformations with dot notation
        while self.match(TokenType.DOT):
            self.advance()
            trans_name = self.consume(TokenType.IDENTIFIER).value
            args = []
            
            if self.match(TokenType.LPAREN):
                self.advance()
                while not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    if self.match(TokenType.COMMA):
                        self.advance()
                self.consume(TokenType.RPAREN)
            
            transformations.append(FunctionCallNode(trans_name, args))
        
        return RagaDeclarationNode(name, source, transformations)
    
    def parse_mandal(self):
        """Parse circular data structure"""
        self.consume(TokenType.MANDAL)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.ASSIGN)
        self.consume(TokenType.LBRACKET)
        
        elements = []
        while not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.consume(TokenType.RBRACKET)
        return MandalDeclarationNode(name, elements)
    
    def parse_seva(self):
        """Parse service/API definition"""
        self.consume(TokenType.SEVA)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LPAREN)
        
        params = []
        while not self.match(TokenType.RPAREN):
            params.append(self.consume(TokenType.IDENTIFIER).value)
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.LBRACE)
        
        body = []
        while not self.match(TokenType.RBRACE):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.RBRACE)
        return SevaDefinitionNode(name, params, body)
    
    def parse_expression(self):
        return self.parse_comparison()
    
    def parse_comparison(self):
        left = self.parse_addition()
        
        while self.match(TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS_THAN, 
                         TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            op = self.current_token().value
            self.advance()
            right = self.parse_addition()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_addition(self):
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current_token().value
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_multiplication(self):
        left = self.parse_postfix()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.current_token().value
            self.advance()
            right = self.parse_postfix()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_postfix(self):
        """Handle property access and method calls"""
        left = self.parse_primary()
        
        while True:
            if self.match(TokenType.DOT):
                self.advance()
                property_name = self.consume(TokenType.IDENTIFIER).value
                
                # Method call
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = []
                    while not self.match(TokenType.RPAREN):
                        args.append(self.parse_expression())
                        if self.match(TokenType.COMMA):
                            self.advance()
                    self.consume(TokenType.RPAREN)
                    left = MethodCallNode(left, property_name, args)
                else:
                    # Property access
                    left = PropertyAccessNode(left, property_name)
            else:
                break
        
        return left
    
    def parse_primary(self):
        # Numbers
        if self.match(TokenType.NUMBER):
            value = float(self.current_token().value)
            self.advance()
            return NumberNode(value)
        
        # Strings
        if self.match(TokenType.STRING):
            value = self.current_token().value
            self.advance()
            return StringNode(value)
        
        # Booleans
        if self.match(TokenType.SATY):
            self.advance()
            return BooleanNode(True)
        
        if self.match(TokenType.ASATY):
            self.advance()
            return BooleanNode(False)
        
        # Null
        if self.match(TokenType.SHUNYA):
            self.advance()
            return NullNode()
        
        # Arrays
        # Arrays
        # In your parser.py, in the parse_primary() method, replace the array parsing section with:

# Arrays
        if self.match(TokenType.LBRACKET):
            self.advance()
            elements = []
            
            # Handle empty array
            if self.match(TokenType.RBRACKET):
                self.advance()
                return ArrayNode(elements)
            
            # Parse elements
            while True:
                elements.append(self.parse_expression())
                
                if self.match(TokenType.COMMA):
                    self.advance()
                    # Skip any newlines after comma
                    self.skip_newlines()
                elif self.match(TokenType.RBRACKET):
                    break
                else:
                    raise SyntaxError(f"Expected ',' or ']' in array, got {self.current_token().type}")
            
            self.consume(TokenType.RBRACKET)
            return ArrayNode(elements)
        
        # Identifiers and function calls
        if self.match(TokenType.IDENTIFIER):
            name = self.current_token().value
            self.advance()
            
            # Function call
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                while not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    if self.match(TokenType.COMMA):
                        self.advance()
                self.consume(TokenType.RPAREN)
                return FunctionCallNode(name, args)
            
            return IdentifierNode(name)
        
        # Parentheses
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return expr
        
        raise SyntaxError(f"Unexpected token: {self.current_token().type} at line {self.current_token().line}")
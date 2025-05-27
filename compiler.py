# File: compiler.py - Core Compiler Logic

import ply.lex as lex
import ply.yacc as yacc
from pygments import highlight
from pygments.lexers import CLexer
from pygments.formatters import HtmlFormatter

class MiniCCompiler:
    def __init__(self):
        self.tokens = []
        self.ast = None
        self.tac = []
        self.symbol_table = {}
        self.temp_count = 0
        self.label_count = 0
        self.errors = []
        self.lexer = None
        self.parser = None
        self._build_lexer()
        self._build_parser()
    
    # Lexer Implementation
    tokens = (
        'INT', 'FLOAT', 'CHAR', 'VOID',
        'IF', 'ELSE', 'WHILE', 'FOR', 'RETURN',
        'ID', 'NUMBER', 'STRING',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'ASSIGN', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
        'AND', 'OR', 'NOT',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
        'SEMI', 'COMMA',
        'PLUSPLUS', 'MINUSMINUS'
    )
    
    # Reserved words
    reserved = {
        'int': 'INT',
        'float': 'FLOAT',
        'char': 'CHAR',
        'void': 'VOID',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'return': 'RETURN',
    }
    
    # Token rules
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'%'
    t_ASSIGN = r'='
    t_EQ = r'=='
    t_NE = r'!='
    t_LT = r'<'
    t_LE = r'<='
    t_GT = r'>'
    t_GE = r'>='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_SEMI = r';'
    t_COMMA = r','
    t_PLUSPLUS = r'\+\+'
    t_MINUSMINUS = r'--'
    
    # Ignored characters (spaces and tabs)
    t_ignore = ' \t'
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t
    
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t
    
    def t_STRING(self, t):
        r'"([^"\\]|\\.)*"'
        t.value = t.value[1:-1]  # Remove quotes
        return t
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_COMMENT(self, t):
        r'//.*'
        pass  # No return value. Token discarded
    
    def t_error(self, t):
        self.errors.append(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)
    
    def _build_lexer(self):
        self.lexer = lex.lex(module=self)
    
    # Parser Implementation
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE'),
        ('left', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MODULO'),
        ('right', 'UMINUS', 'NOT'),
    )
    
    def p_program(self, p):
        '''program : declaration_list'''
        p[0] = ('program', p[1])
    
    def p_declaration_list(self, p):
        '''declaration_list : declaration_list declaration
                           | declaration'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]
    
    def p_declaration(self, p):
        '''declaration : var_declaration
                      | fun_declaration'''
        p[0] = p[1]
    
    def p_var_declaration(self, p):
        '''var_declaration : type_specifier ID SEMI
                          | type_specifier ID LBRACKET NUMBER RBRACKET SEMI'''
        if len(p) == 4:
            p[0] = ('var_decl', p[1], p[2])
            self.symbol_table[p[2]] = {'type': p[1], 'kind': 'variable'}
        else:
            p[0] = ('array_decl', p[1], p[2], p[4])
            self.symbol_table[p[2]] = {'type': p[1], 'kind': 'array', 'size': p[4]}
    
    def p_type_specifier(self, p):
        '''type_specifier : INT
                         | FLOAT
                         | CHAR
                         | VOID'''
        p[0] = p[1]
    
    def p_fun_declaration(self, p):
        '''fun_declaration : type_specifier ID LPAREN params RPAREN compound_stmt'''
        p[0] = ('fun_decl', p[1], p[2], p[4], p[6])
        self.symbol_table[p[2]] = {'type': p[1], 'kind': 'function', 'params': p[4]}
    
    def p_params(self, p):
        '''params : param_list
                 | VOID
                 | empty'''
        p[0] = p[1] if p[1] != 'void' else []
    
    def p_param_list(self, p):
        '''param_list : param_list COMMA param
                     | param'''
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]
    
    def p_param(self, p):
        '''param : type_specifier ID
                | type_specifier ID LBRACKET RBRACKET'''
        if len(p) == 3:
            p[0] = ('param', p[1], p[2])
        else:
            p[0] = ('array_param', p[1], p[2])
    
    def p_compound_stmt(self, p):
        '''compound_stmt : LBRACE local_declarations statement_list RBRACE'''
        p[0] = ('compound', p[2], p[3])
    
    def p_local_declarations(self, p):
        '''local_declarations : local_declarations var_declaration
                             | empty'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []
    
    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                         | empty'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []
    
    def p_statement(self, p):
        '''statement : expression_stmt
                    | compound_stmt
                    | selection_stmt
                    | iteration_stmt
                    | return_stmt'''
        p[0] = p[1]
    
    def p_expression_stmt(self, p):
        '''expression_stmt : expression SEMI
                          | SEMI'''
        if len(p) == 3:
            p[0] = ('expr_stmt', p[1])
        else:
            p[0] = ('empty_stmt',)
    
    def p_selection_stmt(self, p):
        '''selection_stmt : IF LPAREN expression RPAREN statement
                         | IF LPAREN expression RPAREN statement ELSE statement'''
        if len(p) == 6:
            p[0] = ('if', p[3], p[5])
        else:
            p[0] = ('if_else', p[3], p[5], p[7])
    
    def p_iteration_stmt(self, p):
        '''iteration_stmt : WHILE LPAREN expression RPAREN statement'''
        p[0] = ('while', p[3], p[5])
    
    def p_return_stmt(self, p):
        '''return_stmt : RETURN SEMI
                      | RETURN expression SEMI'''
        if len(p) == 3:
            p[0] = ('return',)
        else:
            p[0] = ('return', p[2])
    
    def p_expression(self, p):
        '''expression : var ASSIGN expression
                     | simple_expression'''
        if len(p) == 4:
            p[0] = ('assign', p[1], p[3])
        else:
            p[0] = p[1]
    
    def p_var(self, p):
        '''var : ID
              | ID LBRACKET expression RBRACKET'''
        if len(p) == 2:
            p[0] = ('var', p[1])
        else:
            p[0] = ('array_ref', p[1], p[3])
    
    def p_simple_expression(self, p):
        '''simple_expression : additive_expression relop additive_expression
                            | additive_expression'''
        if len(p) == 4:
            p[0] = ('binop', p[2], p[1], p[3])
        else:
            p[0] = p[1]
    
    def p_relop(self, p):
        '''relop : LE
                | LT
                | GT
                | GE
                | EQ
                | NE'''
        p[0] = p[1]
    
    def p_additive_expression(self, p):
        '''additive_expression : additive_expression addop term
                              | term'''
        if len(p) == 4:
            p[0] = ('binop', p[2], p[1], p[3])
        else:
            p[0] = p[1]
    
    def p_addop(self, p):
        '''addop : PLUS
                | MINUS'''
        p[0] = p[1]
    
    def p_term(self, p):
        '''term : term mulop factor
               | factor'''
        if len(p) == 4:
            p[0] = ('binop', p[2], p[1], p[3])
        else:
            p[0] = p[1]
    
    def p_mulop(self, p):
        '''mulop : TIMES
                | DIVIDE
                | MODULO'''
        p[0] = p[1]
    
    def p_factor(self, p):
        '''factor : LPAREN expression RPAREN
                 | var
                 | call
                 | NUMBER'''
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]
    
    def p_call(self, p):
        '''call : ID LPAREN args RPAREN'''
        p[0] = ('call', p[1], p[3])
    
    def p_args(self, p):
        '''args : arg_list
               | empty'''
        p[0] = p[1] if p[1] else []
    
    def p_arg_list(self, p):
        '''arg_list : arg_list COMMA expression
                   | expression'''
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]
    
    def p_empty(self, p):
        '''empty :'''
        pass
    
    def p_error(self, p):
        if p:
            self.errors.append(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
        else:
            self.errors.append("Syntax error at EOF")
    
    def _build_parser(self):
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)
    
    # Three-Address Code Generation
    def generate_tac(self, node):
        if not node:
            return []
        
        if isinstance(node, (int, float)):
            return str(node)
        
        if isinstance(node, str):
            return node
        
        if not isinstance(node, tuple):
            return str(node)
        
        node_type = node[0]
        
        if node_type == 'program':
            for decl in node[1]:
                self.generate_tac(decl)
        
        elif node_type == 'var_decl':
            self.tac.append(f"declare {node[2]} as {node[1]}")
        
        elif node_type == 'array_decl':
            self.tac.append(f"declare {node[2]}[{node[3]}] as {node[1]}")
        
        elif node_type == 'fun_decl':
            self.tac.append(f"function {node[2]}:")
            self.generate_tac(node[4])  # compound statement
        
        elif node_type == 'compound':
            for decl in node[1]:
                self.generate_tac(decl)
            for stmt in node[2]:
                self.generate_tac(stmt)
        
        elif node_type == 'assign':
            rhs = self.generate_tac(node[2])
            lhs = self.generate_tac(node[1])
            self.tac.append(f"{lhs} = {rhs}")
        
        elif node_type == 'binop':
            left = self.generate_tac(node[2])
            right = self.generate_tac(node[3])
            temp = f"t{self.temp_count}"
            self.temp_count += 1
            self.tac.append(f"{temp} = {left} {node[1]} {right}")
            return temp
        
        elif node_type == 'var':
            return node[1]
        
        elif node_type == 'array_ref':
            index = self.generate_tac(node[2])
            return f"{node[1]}[{index}]"
        
        elif node_type == 'if':
            cond = self.generate_tac(node[1])
            label_false = f"L{self.label_count}"
            self.label_count += 1
            self.tac.append(f"ifnot {cond} goto {label_false}")
            self.generate_tac(node[2])
            self.tac.append(f"{label_false}:")
        
        elif node_type == 'if_else':
            cond = self.generate_tac(node[1])
            label_false = f"L{self.label_count}"
            label_end = f"L{self.label_count + 1}"
            self.label_count += 2
            self.tac.append(f"ifnot {cond} goto {label_false}")
            self.generate_tac(node[2])
            self.tac.append(f"goto {label_end}")
            self.tac.append(f"{label_false}:")
            self.generate_tac(node[3])
            self.tac.append(f"{label_end}:")
        
        elif node_type == 'while':
            label_start = f"L{self.label_count}"
            label_end = f"L{self.label_count + 1}"
            self.label_count += 2
            self.tac.append(f"{label_start}:")
            cond = self.generate_tac(node[1])
            self.tac.append(f"ifnot {cond} goto {label_end}")
            self.generate_tac(node[2])
            self.tac.append(f"goto {label_start}")
            self.tac.append(f"{label_end}:")
        
        elif node_type == 'call':
            args = []
            for arg in node[2]:
                args.append(self.generate_tac(arg))
            for arg in args:
                self.tac.append(f"param {arg}")
            temp = f"t{self.temp_count}"
            self.temp_count += 1
            self.tac.append(f"{temp} = call {node[1]} {len(args)}")
            return temp
        
        elif node_type == 'return':
            if len(node) > 1:
                val = self.generate_tac(node[1])
                self.tac.append(f"return {val}")
            else:
                self.tac.append("return")
        
        elif node_type == 'expr_stmt':
            self.generate_tac(node[1])
    
    def format_ast(self, node, indent=0):
        if not node:
            return ""
        
        if isinstance(node, (int, float, str)):
            return "  " * indent + str(node) + "\n"
        
        if isinstance(node, tuple):
            result = "  " * indent + node[0] + "\n"
            for child in node[1:]:
                if isinstance(child, list):
                    for item in child:
                        result += self.format_ast(item, indent + 1)
                else:
                    result += self.format_ast(child, indent + 1)
            return result
        
        return "  " * indent + str(node) + "\n"
    
    def compile(self, source_code):
        # Reset state
        self.tokens = []
        self.ast = None
        self.tac = []
        self.symbol_table = {}
        self.temp_count = 0
        self.label_count = 0
        self.errors = []
        
        result = {
            'tokens': [],
            'ast': '',
            'tac': [],
            'symbol_table': {},
            'errors': [],
            'highlighted_code': ''
        }
        
        try:
            # Syntax highlighting
            result['highlighted_code'] = highlight(
                source_code, 
                CLexer(), 
                HtmlFormatter(style='default', noclasses=True)
            )
            
            # Lexical Analysis
            self.lexer.input(source_code)
            tokens = []
            while True:
                tok = self.lexer.token()
                if not tok:
                    break
                tokens.append({
                    'type': tok.type,
                    'value': str(tok.value),
                    'line': tok.lineno
                })
            result['tokens'] = tokens
            
            # Syntax Analysis
            self.lexer.input(source_code)  # Reset lexer
            self.ast = self.parser.parse(source_code, lexer=self.lexer)
            
            if self.ast:
                result['ast'] = self.format_ast(self.ast)
                
                # Code Generation
                self.generate_tac(self.ast)
                result['tac'] = self.tac
                result['symbol_table'] = self.symbol_table
            
            result['errors'] = self.errors
            
        except Exception as e:
            result['errors'].append(f"Compilation failed: {str(e)}")
        
        return result

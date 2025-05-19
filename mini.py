
import ply.lex as lex
import ply.yacc as yacc

# --------------------------------------
# LEXICAL ANALYSIS
# --------------------------------------
tokens = (
    'ID', 'NUMBER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQ', 'ASSIGN',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'SEMI',
    'IF', 'ELSE', 'WHILE', 'INT'
)

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'int': 'INT'
}

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQ = r'=='
t_ASSIGN = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI = r';'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    print(f"[LEXER] Token: ({t.type}, {t.value})")
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    print(f"[LEXER] Token: (NUMBER, {t.value})")
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# --------------------------------------
# PARSING and AST GENERATION
# --------------------------------------
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE')
)

symbol_table = {}

# AST node types
class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children or []
        self.value = value
    def __repr__(self):
        return f"Node({self.type}, {self.value}, {self.children})"

def p_program(p):
    '''program : decls statements'''
    p[0] = Node('program', [p[1], p[2]])

def p_decls(p):
    '''decls : decls decl
             | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_decl(p):
    '''decl : INT ID SEMI'''
    symbol_table[p[2]] = 0
    p[0] = Node('decl', value=p[2])

def p_statements(p):
    '''statements : statements statement
                  | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_statement_assign(p):
    'statement : ID ASSIGN expr SEMI'
    p[0] = Node('assign', [p[3]], p[1])

def p_statement_if(p):
    '''statement : IF LPAREN expr RPAREN LBRACE statements RBRACE'''
    p[0] = Node('if', [p[3], Node('block', p[6])])

def p_statement_if_else(p):
    '''statement : IF LPAREN expr RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE'''
    p[0] = Node('if-else', [p[3], Node('block', p[6]), Node('block', p[10])])

def p_statement_while(p):
    '''statement : WHILE LPAREN expr RPAREN LBRACE statements RBRACE'''
    p[0] = Node('while', [p[3], Node('block', p[6])])

def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    p[0] = Node('binop', [p[1], p[3]], p[2])

def p_expr_number(p):
    'expr : NUMBER'
    p[0] = Node('num', value=p[1])

def p_expr_id(p):
    'expr : ID'
    p[0] = Node('var', value=p[1])

def p_empty(p):
    'empty :'
    p[0] = []

def p_error(p):
    print("Syntax error!")

parser = yacc.yacc()

# --------------------------------------
# INTERMEDIATE CODE GENERATION
# --------------------------------------
temp_count = 0

def new_temp():
    global temp_count
    temp = f"t{temp_count}"
    temp_count += 1
    return temp

def generate_code(node):
    if node.type == 'program':
        code = []
        for child in node.children:
            for stmt in child:
                code += generate_code(stmt)
        return code
    elif node.type == 'assign':
        rhs_code, result = generate_code(node.children[0])
        return rhs_code + [f"{node.value} = {result}"]
    elif node.type == 'binop':
        code1, left = generate_code(node.children[0])
        code2, right = generate_code(node.children[1])
        temp = new_temp()
        return code1 + code2 + [f"{temp} = {left} {node.value} {right}"], temp
    elif node.type == 'num':
        return [], str(node.value)
    elif node.type == 'var':
        return [], node.value
    elif node.type == 'if':
        cond_code, cond = generate_code(node.children[0])
        then_code = []
        for stmt in node.children[1].children:
            then_code += generate_code(stmt)
        label_end = new_temp()
        return cond_code + [f"ifnot {cond} goto {label_end}"] + then_code + [f"label {label_end}"]
    elif node.type == 'if-else':
        cond_code, cond = generate_code(node.children[0])
        then_code = []
        else_code = []
        for stmt in node.children[1].children:
            then_code += generate_code(stmt)
        for stmt in node.children[2].children:
            else_code += generate_code(stmt)
        label_else = new_temp()
        label_end = new_temp()
        return cond_code + [f"ifnot {cond} goto {label_else}"] + then_code + [f"goto {label_end}", f"label {label_else}"] + else_code + [f"label {label_end}"]
    elif node.type == 'while':
        label_start = new_temp()
        label_end = new_temp()
        cond_code, cond = generate_code(node.children[0])
        body_code = []
        for stmt in node.children[1].children:
            body_code += generate_code(stmt)
        return [f"label {label_start}"] + cond_code + [f"ifnot {cond} goto {label_end}"] + body_code + [f"goto {label_start}", f"label {label_end}"]
    else:
        return []

# --------------------------------------
# MAIN
# --------------------------------------
if __name__ == '__main__':
    code = '''
    int x;
    x = 5 + 3;
    if (x) {
        x = x - 1;
    } else {
        x = x + 1;
    }
    '''
    print("\n===== Lexical Analysis =====")
    lexer.input(code)
    while True:
        tok = lexer.token()
        if not tok:
            break

    print("\n===== Parsing and AST =====")
    ast = parser.parse(code)
    print(ast)

    print("\n===== Semantic Analysis (Symbol Table) =====")
    print(symbol_table)

    print("\n===== Intermediate Code =====")
    tac = generate_code(ast)
    for line in tac:
        print(line)

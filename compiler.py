import ply.lex as lex
import ply.yacc as yacc

# Lexer
tokens = (
    'ID', 'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQ', 'ASSIGN', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'SEMI', 'COMMA', 'LBRACKET', 'RBRACKET',
    'IF', 'ELSE', 'WHILE', 'INT', 'RETURN', 'VOID'
)

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'int': 'INT',
    'return': 'RETURN',
    'void': 'VOID'
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
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Parser
def p_program(p):
    'program : functions'
    p[0] = {'type': 'program', 'functions': p[1]}

def p_functions(p):
    '''functions : function
                 | functions function'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_function(p):
    'function : type ID LPAREN params RPAREN LBRACE statements RBRACE'
    p[0] = {
        'type': 'function',
        'return_type': p[1],
        'name': p[2],
        'params': p[4],
        'body': p[7]
    }

def p_params(p):
    '''params : param_list
              | VOID
              | empty'''
    if p.slice[1].type in ('VOID', 'empty'):
        p[0] = []
    else:
        p[0] = p[1]

def p_param_list(p):
    '''param_list : param
                  | param_list COMMA param'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_param(p):
    'param : type ID'
    p[0] = {'type': 'param', 'data_type': p[1], 'name': p[2]}

def p_type(p):
    '''type : INT
            | VOID'''
    p[0] = p[1]

def p_statements(p):
    '''statements : statement
                  | statements statement'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_statement(p):
    '''statement : decl
                 | expression SEMI
                 | RETURN expression SEMI
                 | RETURN SEMI
                 | if_statement
                 | while_statement'''
    if p.slice[1].type == 'RETURN':
        if len(p) == 3:
            p[0] = {'type': 'return'}
        elif len(p) == 4:
            p[0] = {'type': 'return', 'value': p[2]}
    elif len(p) == 3:
        p[0] = {'type': 'expression_stmt', 'expr': p[1]}
    else:
        p[0] = p[1]

def p_decl(p):
    '''decl : type ID SEMI
            | type ID LBRACKET NUMBER RBRACKET SEMI'''
    if len(p) == 4:
        p[0] = {'type': 'var_decl', 'data_type': p[1], 'name': p[2]}
    else:
        if p[4] <= 0:
            raise SyntaxError(f"Array size must be positive (got {p[4]})")
        p[0] = {'type': 'array_decl', 'data_type': p[1], 'name': p[2], 'size': p[4]}

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN LBRACE statements RBRACE
                   | IF LPAREN expression RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE'''
    if len(p) == 8:
        p[0] = {'type': 'if', 'condition': p[3], 'body': p[6]}
    else:
        p[0] = {'type': 'if_else', 'condition': p[3], 'if_body': p[6], 'else_body': p[10]}

def p_while_statement(p):
    'while_statement : WHILE LPAREN expression RPAREN LBRACE statements RBRACE'
    p[0] = {'type': 'while', 'condition': p[3], 'body': p[6]}

def p_expression(p):
    '''expression : expression PLUS expression
                 | expression MINUS expression
                 | expression TIMES expression
                 | expression DIVIDE expression
                 | expression EQ expression
                 | ID ASSIGN expression
                 | ID LBRACKET expression RBRACKET ASSIGN expression
                 | ID LPAREN args RPAREN
                 | ID LBRACKET expression RBRACKET
                 | NUMBER
                 | ID'''
    if len(p) == 4 and p[2] == '=':
        p[0] = {'type': 'assign', 'target': p[1], 'value': p[3]}
    elif len(p) == 4:
        p[0] = {'type': 'binop', 'op': p[2], 'left': p[1], 'right': p[3]}
    elif len(p) == 7:
        p[0] = {'type': 'array_assign', 'array': p[1], 'index': p[3], 'value': p[6]}
    elif len(p) == 5:
        if p[2] == '(':
            p[0] = {'type': 'func_call', 'name': p[1], 'args': p[3]}
        else:
            p[0] = {'type': 'array_access', 'array': p[1], 'index': p[3]}
    else:
        if isinstance(p[1], int):
            p[0] = {'type': 'number', 'value': p[1]}
        else:
            p[0] = {'type': 'id', 'value': p[1]}

def p_args(p):
    '''args : arg_list
            | empty'''
    p[0] = p[1]

def p_arg_list(p):
    '''arg_list : expression
                | arg_list COMMA expression'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_empty(p):
    'empty :'
    p[0] = []

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at token '{p.value}' (type {p.type}), line {p.lineno}")
    else:
        raise SyntaxError("Syntax error at EOF")

# Intermediate Code Generation
temp_count = 0
label_count = 0

def new_temp():
    global temp_count
    temp = f"t{temp_count}"
    temp_count += 1
    return temp

def new_label():
    global label_count
    label = f"L{label_count}"
    label_count += 1
    return label

def generate_code(node):
    if node is None:
        return [], None
    if isinstance(node, list):
        code = []
        for item in node:
            c, _ = generate_code(item)
            code += c
        return code, None

    node_type = node.get('type')

    if node_type == 'program':
        return generate_code(node.get('functions', []))

    elif node_type == 'function':
        header = [f"func {node['name']}:"]
        param_code, _ = generate_code(node.get('params', []))
        body_code, _ = generate_code(node.get('body', []))
        return header + param_code + body_code, None

    elif node_type == 'param':
        return [f"param {node['name']}"], None

    elif node_type == 'var_decl':
        return [f"var {node['name']}"], None

    elif node_type == 'array_decl':
        return [f"array {node['name']} {node['size']}"], None

    elif node_type == 'expression_stmt':
        code, _ = generate_code(node['expr'])
        return code, None

    elif node_type == 'assign':
        code, val = generate_code(node['value'])
        return code + [f"{node['target']} = {val}"], None

    elif node_type == 'binop':
        left_code, left = generate_code(node['left'])
        right_code, right = generate_code(node['right'])
        temp = new_temp()
        return left_code + right_code + [f"{temp} = {left} {node['op']} {right}"], temp

    elif node_type == 'number':
        temp = new_temp()
        return [f"{temp} = {node['value']}"], temp

    elif node_type == 'id':
        return [], node['value']

    elif node_type == 'return':
        if 'value' in node:
            code, val = generate_code(node['value'])
            return code + [f"return {val}"], None
        return ["return"], None

    elif node_type == 'if':
        cond_code, cond = generate_code(node['condition'])
        body_code, _ = generate_code(node['body'])
        label_end = new_label()
        return cond_code + [f"ifnot {cond} goto {label_end}"] + body_code + [f"label {label_end}"], None

    elif node_type == 'if_else':
        cond_code, cond = generate_code(node['condition'])
        if_code, _ = generate_code(node['if_body'])
        else_code, _ = generate_code(node['else_body'])
        label_else = new_label()
        label_end = new_label()
        return (
            cond_code + [f"ifnot {cond} goto {label_else}"] + if_code +
            [f"goto {label_end}", f"label {label_else}"] + else_code + [f"label {label_end}"],
            None
        )

    elif node_type == 'while':
        label_start = new_label()
        label_end = new_label()
        cond_code, cond = generate_code(node['condition'])
        body_code, _ = generate_code(node['body'])
        return (
            [f"label {label_start}"] + cond_code +
            [f"ifnot {cond} goto {label_end}"] + body_code +
            [f"goto {label_start}", f"label {label_end}"],
            None
        )

    elif node_type == 'func_call':
        arg_code = []
        arg_vals = []
        for arg in node['args']:
            ac, av = generate_code(arg)
            arg_code += ac
            arg_vals.append(av)
        temp = new_temp()
        return arg_code + [f"{temp} = call {node['name']} " + " ".join(arg_vals)], temp

    elif node_type == 'array_access':
        idx_code, idx = generate_code(node['index'])
        temp = new_temp()
        return idx_code + [f"{temp} = {node['array']}[{idx}]"], temp

    elif node_type == 'array_assign':
        idx_code, idx = generate_code(node['index'])
        val_code, val = generate_code(node['value'])
        return idx_code + val_code + [f"{node['array']}[{idx}] = {val}"], None

    else:
        return [f"ERROR: Unknown node type {node_type}"], None

# Build
lexer = lex.lex()
parser = yacc.yacc()

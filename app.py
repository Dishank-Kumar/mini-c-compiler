from flask import Flask, render_template, request
from compiler import lexer, parser, generate_code
from pygments import highlight
from pygments.lexers import CLexer
from pygments.formatters import HtmlFormatter
import json

app = Flask(__name__)

def format_ast(node, indent=0):
    """Recursively format AST as a tree structure"""
    if isinstance(node, dict):
        lines = []
        lines.append("  " * indent + "{")
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                lines.append("  " * (indent+1) + f'"{key}":')
                lines.append(format_ast(value, indent+1))
            else:
                lines.append("  " * (indent+1) + f'"{key}": {repr(value)}')
        lines.append("  " * indent + "}")
        return "\n".join(lines)
    elif isinstance(node, list):
        lines = []
        lines.append("  " * indent + "[")
        for item in node:
            lines.append(format_ast(item, indent+1))
        lines.append("  " * indent + "]")
        return ",\n".join(lines)
    else:
        return "  " * indent + repr(node)

def flatten_tac(tac):
    flat = []
    for item in tac:
        if isinstance(item, list):
            flat.extend(flatten_tac(item))
        elif isinstance(item, tuple):
            flat.extend(flatten_tac(item[0]))
        elif isinstance(item, str):
            flat.append(item)
    return flat

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        code = request.form.get('code', '')
        
        # Lexical analysis
        lexer.input(code)
        tokens = []
        try:
            while True:
                tok = lexer.token()
                if not tok:
                    break
                tokens.append((tok.type, tok.value))
        except Exception as e:
            tokens = [('ERROR', f"Lexer error: {str(e)}")]

        # Parsing and AST formatting
        ast = ""
        ast_str = ""
        try:
            ast = parser.parse(code)
            if isinstance(ast, (dict, list)):
                ast_str = format_ast(ast)  # Use our custom formatter
                # Alternatively: ast_str = json.dumps(ast, indent=2)
            else:
                ast_str = str(ast)
        except Exception as e:
            ast_str = f"Parser error: {str(e)}"

        # Code generation
        tac = []
        try:
            if ast and isinstance(ast, dict):  # Only generate code if parsing succeeded
                tac, _ = generate_code(ast)
        except Exception as e:
            tac = [f"Code generation error: {str(e)}"]

        # Syntax highlighting
        highlighted_code = highlight(code, CLexer(), HtmlFormatter())
        
        return render_template('index.html',
                            tokens=tokens,
                            ast=ast_str,
                            tac=tac,
                            code=highlighted_code,
                            css=HtmlFormatter().get_style_defs(),
                            input_code=code)
    
    # Default code to show in editor
    default_code = """int main() {
    int arr[10];
    arr[0] = 5;
    return arr[0];
}"""
    return render_template('index.html', input_code=default_code)

if __name__ == '__main__':
    app.run(debug=True)
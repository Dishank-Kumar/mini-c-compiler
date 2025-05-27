from flask import Flask, render_template, request, jsonify
import os
from compiler import MiniCCompiler

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    try:
        source_code = request.form.get('source_code', '')
        
        if not source_code.strip():
            return render_template('index.html', 
                                 error="Please enter some code to compile.")
        
        compiler = MiniCCompiler()
        result = compiler.compile(source_code)
        
        return render_template('index.html', 
                             source_code=source_code,
                             result=result)
                             
    except Exception as e:
        return render_template('index.html', 
                             source_code=source_code if 'source_code' in locals() else '',
                             error=f"Compilation Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


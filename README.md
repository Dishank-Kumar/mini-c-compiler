# 🛠️ Mini Compiler in Python using PLY

This is a simple **compiler front-end** built with **Python** using the **PLY (Python Lex-Yacc)** library. It performs essential compilation stages including lexical analysis, parsing, AST construction, symbol table creation, and intermediate code generation (Three-Address Code).

---

## 📚 Introduction

This project demonstrates how to construct a basic compiler using PLY. It parses a subset of C-like language constructs and translates them into an intermediate representation, laying the foundation for building a complete compiler with code optimization and machine code generation.

---

## 🎯 Project Goals

- Learn and implement compiler design principles
- Understand how lexers and parsers work using PLY
- Construct an abstract syntax tree (AST)
- Generate intermediate three-address code (TAC)
- Demonstrate control flow with `if`, `if-else`, and `while` statements

---

## ✅ Features

- Variable declaration support (`int`)
- Arithmetic operations: `+`, `-`, `*`, `/`
- Relational operators: `==` (for future use)
- Control structures:
  - `if`
  - `if-else`
  - `while`
- Symbol table creation
- AST (Abstract Syntax Tree) generation
- Intermediate code generation (Three-Address Code)

---

## 🧱 Components

- **Lexer**: Tokenizes the input source code.
- **Parser**: Uses grammar rules to build an AST.
- **AST Generator**: Constructs a hierarchical structure of code.
- **Semantic Analysis**: Builds a symbol table.
- **Code Generator**: Produces intermediate code in TAC form.

---

## 📦 Requirements

- Python 3.x
- PLY (Python Lex-Yacc)

Install dependencies with:

```bash
pip install ply

